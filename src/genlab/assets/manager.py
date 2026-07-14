from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any

from genlab.core.exceptions import AssetError, DownloadError, InsufficientDiskError

_HF_TRANSFER_CHECKED = False
_HF_TRANSFER_AVAILABLE = False
_BANDWIDTH_CACHE: float | None = None
_BANDWIDTH_CACHE_AT = 0.0
_BANDWIDTH_TTL = 300.0


class AssetManager:
    def __init__(self, cache_dir: str | Path, config: dict | None = None):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._config = config or {}

    def resolve(self, provider: Any, strategy: str = "selective") -> str:
        patterns = None if strategy == "full" else provider.get_required_files()
        return self._download(
            repo_id=provider.get_model_id(),
            patterns=patterns,
        )

    def resolve_raw(self, repo_id: str) -> str:
        return self._download(repo_id=repo_id, patterns=None)

    def _snapshot_kwargs(self, repo_id: str, patterns: list[str] | None) -> dict:
        kwargs: dict[str, Any] = dict(
            repo_id=repo_id,
            local_dir=self._cache_dir / repo_id.replace("/", "__"),
        )
        if patterns is not None:
            kwargs["allow_patterns"] = patterns
        return kwargs

    def _resolve_config_key(self, *keys: str) -> Any:
        value: Any = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    @staticmethod
    def hf_transfer_available() -> bool:
        global _HF_TRANSFER_CHECKED, _HF_TRANSFER_AVAILABLE
        if not _HF_TRANSFER_CHECKED:
            try:
                import hf_transfer  # noqa: F401
                _HF_TRANSFER_AVAILABLE = True
            except ImportError:
                _HF_TRANSFER_AVAILABLE = False
            _HF_TRANSFER_CHECKED = True
        return _HF_TRANSFER_AVAILABLE

    def _enable_hf_transfer(self, total_bytes: int) -> None:
        threshold = 500 * 1024 * 1024
        if total_bytes < threshold:
            return
        mode = self._resolve_config_key("download", "hf_transfer")
        if mode == "off":
            return
        if mode == "on" or (mode == "auto" and self.hf_transfer_available()):
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

    def _verify_disk_space(self, required_bytes: int) -> None:
        mode = self._resolve_config_key("download", "verify_space")
        if mode is False:
            return
        try:
            _, _, free = shutil.disk_usage(str(self._cache_dir))
            needed = int(required_bytes * 1.1)
            if free < needed:
                free_gb = free / (1024**3)
                needed_gb = needed / (1024**3)
                raise InsufficientDiskError(
                    f"Espacio insuficiente en {self._cache_dir}: "
                    f"libres {free_gb:.1f} GB, necesarios ~{needed_gb:.1f} GB"
                )
        except InsufficientDiskError:
            raise
        except OSError as exc:
            raise DownloadError(f"No se pudo verificar espacio en disco: {exc}") from exc

    def _download(self, repo_id: str, patterns: list[str] | None) -> str:
        from huggingface_hub import snapshot_download

        estimate = self.estimate_raw(repo_id, patterns)
        self._verify_disk_space(estimate["total_bytes"])
        self._enable_hf_transfer(estimate["total_bytes"])

        target = self._cache_dir / repo_id.replace("/", "__")
        target.mkdir(parents=True, exist_ok=True)

        kwargs = self._snapshot_kwargs(repo_id, patterns)
        snapshot_download(**kwargs)
        return str(target)

    def estimate(self, provider: Any) -> dict[str, Any]:
        return self.estimate_raw(provider.get_model_id(), provider.get_required_files())

    def estimate_raw(self, repo_id: str, patterns: list[str] | None) -> dict[str, Any]:
        from fnmatch import fnmatch
        from huggingface_hub import HfApi

        api = HfApi()
        info = api.model_info(repo_id, files_metadata=True)
        matched = []
        total_bytes = 0
        repo_total = 0
        for s in info.siblings:
            size = s.size or 0
            repo_total += size
            if patterns is None or any(fnmatch(s.rfilename, p) for p in patterns):
                matched.append({
                    "path": s.rfilename,
                    "size_gb": round(size / (1024**3), 2),
                })
                total_bytes += size

        return {
            "repo_id": repo_id,
            "files": matched,
            "total_bytes": total_bytes,
            "total_gb": round(total_bytes / (1024**3), 2),
            "repo_total_bytes": repo_total,
            "repo_total_gb": round(repo_total / (1024**3), 2),
            "file_count": len(matched),
        }

    def _probe_bandwidth(self) -> float:
        global _BANDWIDTH_CACHE, _BANDWIDTH_CACHE_AT
        now = time.monotonic()
        if _BANDWIDTH_CACHE is not None and (now - _BANDWIDTH_CACHE_AT) < _BANDWIDTH_TTL:
            return _BANDWIDTH_CACHE
        try:
            import urllib.request
            test_url = "https://huggingface.co/datasets/glue/resolve/main/README.md"
            chunk_size = 1024 * 1024
            req = urllib.request.Request(test_url, headers={"User-Agent": "genlab-bandwidth-probe/0.1"})
            start = time.monotonic()
            total = 0
            with urllib.request.urlopen(req, timeout=10) as resp:
                while total < chunk_size:
                    data = resp.read(65536)
                    if not data:
                        break
                    total += len(data)
            elapsed = time.monotonic() - start
            bw = total / elapsed / (1024 * 1024) if elapsed > 0 else 0.0
            _BANDWIDTH_CACHE = bw
            _BANDWIDTH_CACHE_AT = now
            return bw
        except Exception:
            pass
        _BANDWIDTH_CACHE = 0.0
        _BANDWIDTH_CACHE_AT = now
        return 0.0

    def probe_bandwidth(self) -> float:
        return self._probe_bandwidth()

    def diagnostic(self, provider: Any) -> dict[str, Any]:
        model_id = provider.get_model_id()
        est = self.estimate(provider)
        cached = self.cached_path(model_id)
        free = self._disk_free_gb()
        bw = self.probe_bandwidth()
        hf_avail = self.hf_transfer_available()
        hf_active = os.environ.get("HF_HUB_ENABLE_HF_TRANSFER") == "1"

        total_bytes = est["total_bytes"]
        time_min = 0.0
        effective_bw = bw if bw > 1.0 else 0.0
        if effective_bw > 0 and total_bytes > 0:
            time_min = (total_bytes / (1024 * 1024)) / effective_bw / 60

        return {
            "model_name": provider.get_metadata().get("model_id", model_id),
            "repo_id": model_id,
            "repo_total_gb": est["repo_total_gb"],
            "download_size_gb": est["total_gb"],
            "file_count": est["file_count"],
            "free_space_gb": free,
            "hf_transfer_available": hf_avail,
            "hf_transfer_active": hf_active,
            "bandwidth_mbps": round(effective_bw, 2),
            "estimated_time_min": round(time_min, 1),
            "cached": cached is not None,
            "cached_path": str(cached) if cached else None,
        }

    def _disk_free_gb(self) -> float:
        try:
            _, _, free = shutil.disk_usage(str(self._cache_dir))
            return round(free / (1024**3), 1)
        except Exception:
            return 0.0

    def cached_path(self, model_id: str) -> Path | None:
        target = self._cache_dir / model_id.replace("/", "__")
        return target if target.is_dir() else None

    def clear(self, model_id: str) -> None:
        target = self._cache_dir / model_id.replace("/", "__")
        if target.is_dir():
            shutil.rmtree(str(target))

    def clear_all(self) -> None:
        for item in self._cache_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(str(item))
