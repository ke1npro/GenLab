from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def export_video(
    frames: list,
    output_dir: str,
    fps: int = 8,
    manifest: dict | None = None,
) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    run_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    video_filename = f"genlab_{timestamp}_{run_id}.mp4"
    video_path = str(output_path / video_filename)

    if frames:
        _write_video(frames, video_path, fps)

    if manifest:
        manifest_path = str(output_path / f"genlab_{timestamp}_{run_id}_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    return video_path


def _write_video(frames: list, path: str, fps: int) -> None:
    try:
        import imageio
    except ImportError:
        raise ImportError("Se necesita imageio-ffmpeg para exportar video. pip install imageio-ffmpeg")

    writer = imageio.get_writer(path, fps=fps, codec="libx264", quality=8)
    for frame in frames:
        writer.append_data(frame)
    writer.close()
