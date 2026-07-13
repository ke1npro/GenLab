from pathlib import Path

import pytest

from genlab.assets.manager import AssetManager
from genlab.core.exceptions import InsufficientDiskError


class FakeProvider:
    def get_model_id(self):
        return "test/model"

    def get_required_files(self):
        return ["*.json", "data/*"]

    def get_metadata(self):
        return {"model_id": "Test Model"}


class FakeSibling:
    def __init__(self, path: str, size: int = 0):
        self.rfilename = path
        self.size = size


def test_init_creates_cache_dir(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    assert (tmp_path / "cache").is_dir()


def test_cached_path_not_found(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    assert am.cached_path("nonexistent/model") is None


def test_cached_path_found(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    repo_dir = tmp_path / "cache" / "nonexistent__model"
    repo_dir.mkdir(parents=True)
    result = am.cached_path("nonexistent/model")
    assert result == repo_dir


def test_hf_transfer_available_returns_bool(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    result = am.hf_transfer_available()
    assert isinstance(result, bool)


def test_verify_disk_space_passes(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    am._verify_disk_space(1)  # 1 byte should always fit


def test_verify_disk_space_disabled(tmp_path):
    am = AssetManager(str(tmp_path / "cache"), config={"download": {"verify_space": False}})
    am._verify_disk_space(10**30)  # should not raise


def test_resolve_config_key(tmp_path):
    am = AssetManager(str(tmp_path / "cache"), config={"download": {"hf_transfer": "on"}})
    assert am._resolve_config_key("download", "hf_transfer") == "on"


def test_resolve_config_key_none(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    assert am._resolve_config_key("nonexistent", "key") is None


def test_diagnostic_structure(tmp_path, monkeypatch):
    hf = pytest.importorskip("huggingface_hub", reason="huggingface-hub no instalado")
    HfApi = hf.HfApi

    class FakeInfo:
        siblings = [
            FakeSibling("model_index.json", 500),
            FakeSibling("data/weights.bin", 1000 * 1024 * 1024),
            FakeSibling("extra/unused.txt", 200),
        ]

    class FakeApi:
        def model_info(self, repo_id, files_metadata=True):
            return FakeInfo()

    monkeypatch.setattr(HfApi, "model_info", FakeApi.model_info)

    from fnmatch import fnmatch
    monkeypatch.setattr("fnmatch.fnmatch", lambda name, pat: True)

    provider = FakeProvider()
    diag = am.diagnostic(provider)

    assert "model_name" in diag
    assert "repo_id" in diag
    assert "repo_total_gb" in diag
    assert "download_size_gb" in diag
    assert "file_count" in diag
    assert "free_space_gb" in diag
    assert "hf_transfer_available" in diag
    assert "hf_transfer_active" in diag
    assert "cached" in diag
    assert diag["model_name"] == "Test Model"
    assert diag["repo_id"] == "test/model"


def test_symlinks_supported(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    result = am._symlinks_supported()
    assert isinstance(result, bool)


def test_disk_free_gb(tmp_path):
    am = AssetManager(str(tmp_path / "cache"))
    free = am._disk_free_gb()
    assert isinstance(free, (int, float))
    assert free >= 0
