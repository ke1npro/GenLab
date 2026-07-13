import os
import sys
from pathlib import Path

import pytest

from genlab.core.bootstrap import _build_report, _ensure_dirs
from genlab.core.environment import detect_environment, is_colab
from genlab.core.exceptions import (
    ConfigError,
    GenLabError,
    ModelError,
    ModelNotFoundError,
    TaskNotSupportedError,
)
from genlab.core.hardware import check_disk_free, detect_hardware
from genlab.core.paths import resolve_paths


def test_exception_hierarchy():
    assert issubclass(ConfigError, GenLabError)
    assert issubclass(ModelError, GenLabError)
    assert issubclass(ModelNotFoundError, ModelError)
    assert issubclass(TaskNotSupportedError, GenLabError)


def test_detect_environment_returns_dict():
    env = detect_environment()
    assert "type" in env
    assert "is_colab" in env
    assert "is_local" in env


def test_is_colab():
    assert is_colab() is False


def test_detect_hardware_returns_dict():
    hw = detect_hardware()
    assert "gpu" in hw
    assert "vram_gb" in hw
    assert "ram_gb" in hw
    assert "cuda_version" in hw


def test_detect_hardware_no_gpu():
    hw = detect_hardware()
    assert isinstance(hw["has_gpu"], bool)


def test_check_disk_free():
    free = check_disk_free()
    assert isinstance(free, (int, float))
    assert free > 0


def test_resolve_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("COLAB_GPU", "")
    monkeypatch.delenv("COLAB_GPU", raising=False)

    project_root = Path.cwd()
    paths = resolve_paths(config_dir=str(tmp_path / "configs"))
    assert "project_root" in paths
    assert "output_dir" in paths
    assert "cache_dir" in paths
    assert paths["drive_base"] is None


def test_colab_paths(monkeypatch):
    monkeypatch.setenv("COLAB_GPU", "Tesla T4")

    paths = resolve_paths()
    assert paths["drive_base"] is not None

    monkeypatch.delenv("COLAB_GPU")


def test_ensure_dirs_creates_directories(tmp_path):
    paths = {
        "output_dir": str(tmp_path / "outputs"),
        "temp_dir": str(tmp_path / "tmp"),
        "cache_dir": str(tmp_path / "cache"),
        "runs_dir": str(tmp_path / "runs"),
    }
    _ensure_dirs(paths)
    assert (tmp_path / "outputs").is_dir()
    assert (tmp_path / "tmp").is_dir()
    assert (tmp_path / "cache").is_dir()
    assert (tmp_path / "runs").is_dir()


def test_build_report():
    env = {"type": "local", "is_colab": False}
    hw = {"gpu": "N/A", "vram_gb": 0, "ram_gb": 16, "cuda_version": "N/A"}
    paths = {"drive_base": None, "cache_dir": "/tmp/cache"}
    report = _build_report(env, hw, paths, hf_ok=False)
    assert isinstance(report, list)
    assert any("GPU" in row[0] for row in report)
    assert any("RAM" in row[0] for row in report)
