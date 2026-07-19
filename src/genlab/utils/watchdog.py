from __future__ import annotations

import math
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Sample
# ---------------------------------------------------------------------------

@dataclass
class TransferSample:
    timestamp: float
    elapsed: float
    bytes_transferred: int  # cumulative from start
    bytes_delta: int        # bytes since last sample
    speed_mbps: float       # instantaneous


# ---------------------------------------------------------------------------
# Watchdog
# ---------------------------------------------------------------------------

class TransferWatchdog:
    """Monitors a file or directory during transfer, sampling periodically."""

    def __init__(
        self,
        target: str | Path,
        interval: float = 0.5,
        on_sample: Optional[Callable[[TransferSample], None]] = None,
    ):
        self._target = Path(target)
        self._interval = interval
        self._on_sample = on_sample
        self.samples: list[TransferSample] = []
        self._start_bytes: int = 0
        self._start_time: float = 0.0
        self._running = False
        self._thread: threading.Thread | None = None

    # -- public API ---------------------------------------------------------

    @property
    def elapsed(self) -> float:
        if not self.samples:
            return 0.0
        return self.samples[-1].elapsed

    @property
    def total_bytes(self) -> int:
        if not self.samples:
            return 0
        return self.samples[-1].bytes_transferred

    def start(self) -> None:
        self._start_bytes = self._get_current_bytes()
        self._start_time = time.time()
        self._running = True
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join()
        # final sample
        self._take_sample()

    def __enter__(self) -> "TransferWatchdog":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()

    @staticmethod
    def format_bytes(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"

    # -- internals ----------------------------------------------------------

    def _get_current_bytes(self) -> int:
        total = 0
        if self._target.is_file():
            return self._target.stat().st_size
        if self._target.is_dir():
            for root, _, files in os.walk(str(self._target)):
                for f in files:
                    try:
                        total += (Path(root) / f).stat().st_size
                    except OSError:
                        pass
        return total

    def _take_sample(self) -> None:
        current = self._get_current_bytes()
        elapsed = time.time() - self._start_time
        cumulative = current - self._start_bytes

        prev = self.samples[-1] if self.samples else None
        if prev:
            dt = elapsed - prev.elapsed
            db = cumulative - prev.bytes_transferred
        else:
            dt = elapsed
            db = cumulative

        speed = (db / (1024 * 1024)) / dt if dt > 0 else 0.0

        sample = TransferSample(
            timestamp=time.time(),
            elapsed=elapsed,
            bytes_transferred=cumulative,
            bytes_delta=db,
            speed_mbps=speed,
        )
        self.samples.append(sample)
        if self._on_sample:
            self._on_sample(sample)

    def _sample_loop(self) -> None:
        while self._running:
            time.sleep(self._interval)
            self._take_sample()


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

@dataclass
class TransferStats:
    # general
    total_time_s: float
    total_bytes: int
    total_gb: float
    avg_speed_mbps: float

    # distribution
    mean: float
    median: float
    min_speed: float
    max_speed: float
    p5: float
    p95: float

    # variability
    std: float
    variance: float
    cv: float  # coefficient of variation

    # consistency
    thresholds: dict[str, float]  # e.g. {">50 MB/s": 85.2, ...}


def compute_stats(samples: list[TransferSample]) -> TransferStats:
    if not samples:
        raise ValueError("No samples to compute stats from")

    speeds = [s.speed_mbps for s in samples]
    n = len(speeds)
    speeds_sorted = sorted(speeds)

    total_time = samples[-1].elapsed
    total_bytes = samples[-1].bytes_transferred
    total_gb = total_bytes / (1024 ** 3)
    avg_speed = total_gb * 1024 / total_time if total_time > 0 else 0.0

    mean = sum(speeds) / n

    def percentile(sorted_data, p):
        k = (p / 100.0) * (len(sorted_data) - 1)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

    median = percentile(speeds_sorted, 50)
    p5 = percentile(speeds_sorted, 5)
    p95 = percentile(speeds_sorted, 95)
    min_speed = speeds_sorted[0]
    max_speed = speeds_sorted[-1]

    variance = sum((s - mean) ** 2 for s in speeds) / n
    std = math.sqrt(variance)
    cv = std / mean if mean > 0 else 0.0

    # consistency above thresholds
    THRESHOLDS = [50, 75, 100, 110]
    thresholds = {}
    for t in THRESHOLDS:
        pct = sum(1 for s in speeds if s > t) / n * 100
        thresholds[f">{t} MB/s"] = round(pct, 1)

    return TransferStats(
        total_time_s=round(total_time, 2),
        total_bytes=total_bytes,
        total_gb=round(total_gb, 2),
        avg_speed_mbps=round(avg_speed, 2),
        mean=round(mean, 2),
        median=round(median, 2),
        min_speed=round(min_speed, 2),
        max_speed=round(max_speed, 2),
        p5=round(p5, 2),
        p95=round(p95, 2),
        std=round(std, 2),
        variance=round(variance, 2),
        cv=round(cv, 4),
        thresholds=thresholds,
    )


# ---------------------------------------------------------------------------
# Throttling detection
# ---------------------------------------------------------------------------

@dataclass
class ThrottlingEvent:
    start_time: float
    end_time: float
    duration: float
    drop_pct: float  # how much below mean
    avg_during: float


def detect_throttling(
    samples: list[TransferSample],
    mean_speed: float,
    drop_thresholds: list[float] = None,
    min_duration: float = 3.0,
) -> list[ThrottlingEvent]:
    if drop_thresholds is None:
        drop_thresholds = [0.20, 0.30]

    if not samples:
        return []

    events = []
    in_drop = False
    drop_start = 0.0
    drop_speeds: list[float] = []

    for s in samples:
        current_drop = 1.0 - (s.speed_mbps / mean_speed) if mean_speed > 0 else 0

        is_dropped = any(current_drop >= t for t in drop_thresholds)

        if is_dropped and not in_drop:
            in_drop = True
            drop_start = s.elapsed
            drop_speeds = [s.speed_mbps]
        elif is_dropped and in_drop:
            drop_speeds.append(s.speed_mbps)
        elif not is_dropped and in_drop:
            in_drop = False
            duration = s.elapsed - drop_start
            if duration >= min_duration:
                avg_drop = sum(drop_speeds) / len(drop_speeds)
                drop_pct = round((1.0 - avg_drop / mean_speed) * 100, 1) if mean_speed > 0 else 0
                events.append(ThrottlingEvent(
                    start_time=round(drop_start, 1),
                    end_time=round(s.elapsed, 1),
                    duration=round(duration, 1),
                    drop_pct=drop_pct,
                    avg_during=round(avg_drop, 2),
                ))

    # handle drop at end
    if in_drop:
        duration = samples[-1].elapsed - drop_start
        if duration >= min_duration:
            avg_drop = sum(drop_speeds) / len(drop_speeds)
            drop_pct = round((1.0 - avg_drop / mean_speed) * 100, 1) if mean_speed > 0 else 0
            events.append(ThrottlingEvent(
                start_time=round(drop_start, 1),
                end_time=round(samples[-1].elapsed, 1),
                duration=round(duration, 1),
                drop_pct=drop_pct,
                avg_during=round(avg_drop, 2),
            ))

    return events


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def plot_speed_vs_time(samples: list[TransferSample], title: str = "") -> None:
    import matplotlib.pyplot as plt

    times = [s.elapsed for s in samples]
    speeds = [s.speed_mbps for s in samples]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, speeds, linewidth=0.8, alpha=0.8)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("MB/s")
    ax.set_title(title or "Velocidad vs Tiempo")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show()


def plot_histogram(samples: list[TransferSample], title: str = "") -> None:
    import matplotlib.pyplot as plt

    speeds = [s.speed_mbps for s in samples]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.hist(speeds, bins=40, alpha=0.7, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("MB/s")
    ax.set_ylabel("Frecuencia")
    ax.set_title(title or "Distribución de Velocidades")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show()


def plot_boxplot(samples: list[TransferSample], title: str = "") -> None:
    import matplotlib.pyplot as plt

    speeds = [s.speed_mbps for s in samples]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(speeds, vert=False, widths=0.5)
    ax.set_xlabel("MB/s")
    ax.set_title(title or "Boxplot de Velocidades")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(
    label: str,
    stats: TransferStats,
    throttling_events: list[ThrottlingEvent],
) -> None:
    sep = "=" * 55
    sub = "-" * 55

    print()
    print(sep)
    print(f"  {label}")
    print(sep)
    print(f"  Tiempo total:        {stats.total_time_s} s")
    print(f"  Datos transferidos:  {TransferWatchdog.format_bytes(stats.total_bytes)} ({stats.total_gb} GB)")
    print(f"  Velocidad promedio:  {stats.avg_speed_mbps} MB/s")
    print()
    print(sub)
    print("  Velocidad (MB/s)")
    print(sub)
    print(f"  Promedio:            {stats.mean}")
    print(f"  Mediana:             {stats.median}")
    print(f"  Máxima:              {stats.max_speed}")
    print(f"  Mínima:              {stats.min_speed}")
    print(f"  Percentil 95:        {stats.p95}")
    print(f"  Percentil 5:         {stats.p5}")
    print()
    print(sub)
    print("  Variabilidad")
    print(sub)
    print(f"  Desviación std:      {stats.std}")
    print(f"  Varianza:            {stats.variance}")
    print(f"  Coef. variación:     {stats.cv}")
    print()
    print(sub)
    print("  Consistencia")
    print(sub)
    for label_, pct in stats.thresholds.items():
        print(f"  {label_:<20} {pct}%")
    print()
    print(sub)
    print("  Análisis")
    print(sub)
    if throttling_events:
        print(f"  Throttling detectado: SÍ")
        print(f"  Caídas detectadas:    {len(throttling_events)}")
        for ev in throttling_events:
            print(f"    · {ev.duration}s a los {ev.start_time}s "
                  f"(−{ev.drop_pct}%, promedio {ev.avg_during} MB/s)")
    else:
        print(f"  Throttling detectado: NO")
        if stats.cv < 0.15:
            print(f"  Transferencia estable (CV < 15%)")
        elif stats.cv < 0.30:
            print(f"  Transferencia moderadamente variable (CV 15-30%)")
        else:
            print(f"  Transferencia muy variable (CV > 30%)")
    print(sep)
