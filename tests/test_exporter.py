import json
from pathlib import Path

import pytest

from genlab.services.exporter import export_video


def test_export_video_creates_file(tmp_path):
    import PIL.Image
    import numpy as np

    frame = PIL.Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    manifest = {"model": "test", "seed": 42}
    path = export_video(
        frames=[frame, frame, frame],
        output_dir=str(tmp_path),
        fps=8,
        manifest=manifest,
    )
    assert path.startswith(str(tmp_path))


def test_export_video_no_frames(tmp_path):
    path = export_video(
        frames=[],
        output_dir=str(tmp_path),
        fps=8,
        manifest={"test": True},
    )
    assert path.startswith(str(tmp_path))


def test_export_video_manifest_file(tmp_path):
    import PIL.Image
    import numpy as np

    frame = PIL.Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    manifest = {"model": "cogvideo", "seed": 123}
    export_video(
        frames=[frame, frame],
        output_dir=str(tmp_path),
        fps=8,
        manifest=manifest,
    )
    manifests = list(Path(tmp_path).glob("*manifest*"))
    assert len(manifests) >= 1
    data = json.loads(manifests[0].read_text())
    assert data["model"] == "cogvideo"
