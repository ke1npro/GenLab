from __future__ import annotations

from pathlib import Path
from typing import Callable

from genlab.core.environment import detect_environment


def resolve_paths(config_dir: str | Path = "configs") -> dict:
    env = detect_environment()
    base = _find_project_root()
    config_dir = Path(config_dir) if Path(config_dir).is_absolute() else base / config_dir

    if env["is_colab"]:
        return _colab_paths(base, config_dir)
    return _local_paths(base, config_dir)


def _find_project_root() -> Path:
    candidate = Path.cwd()
    for _ in range(5):
        if (candidate / "configs").is_dir() or (candidate / "pyproject.toml").is_file():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


def _colab_paths(project_root: Path, config_dir: Path) -> dict:
    drive_root = Path("/content/drive/MyDrive/GenLab")
    return {
        "project_root": str(project_root),
        "config_dir": str(config_dir),
        "output_dir": str(drive_root / "outputs"),
        "temp_dir": str(Path("/content/tmp")),
        "cache_dir": str(Path("/content/models_cache")),
        "runs_dir": str(drive_root / "outputs" / "runs"),
        "drive_base": str(drive_root),
    }


def _local_paths(project_root: Path, config_dir: Path) -> dict:
    return {
        "project_root": str(project_root),
        "config_dir": str(config_dir),
        "output_dir": str(project_root / "outputs"),
        "temp_dir": str(project_root / "outputs" / "tmp"),
        "cache_dir": str(project_root / "models_cache"),
        "runs_dir": str(project_root / "outputs" / "runs"),
        "drive_base": None,
    }
