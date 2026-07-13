import pytest

from genlab.assets.inspector import ModelInspector


class FakeAssetManager:
    def __init__(self, cached=False):
        self._cached = cached

    def estimate(self, provider):
        return {
            "files": [{"path": "model.bin", "size_gb": 1.0}],
            "total_bytes": 1_000_000_000,
            "total_gb": 0.93,
            "repo_total_gb": 1.0,
            "file_count": 1,
        }

    def cached_path(self, model_id):
        if self._cached:
            return "/fake/cache/path"
        return None

    def diagnostic(self, provider):
        return {
            "model_name": "Fake Model",
            "repo_id": "fake/model",
            "repo_total_gb": 2.0,
            "download_size_gb": 0.93,
            "file_count": 1,
            "free_space_gb": 50.0,
            "hf_transfer_available": True,
            "hf_transfer_active": True,
            "bandwidth_mbps": 10.5,
            "estimated_time_min": 1.5,
            "cached": self._cached,
            "cached_path": "/fake/cache/path" if self._cached else None,
        }


class FakeProvider:
    capabilities = {"supports_text_to_video": True}

    def get_model_id(self):
        return "fake/model"

    def get_required_files(self):
        return ["*.bin"]

    def get_metadata(self):
        return {
            "model_id": "Fake Model",
            "license": "apache-2.0",
            "hardware_compatibility": {"t4": True},
            "estimated_vram_gb": 8,
            "description": "Fake model for testing",
        }


def test_inspect_structure():
    inspector = ModelInspector(FakeAssetManager())
    info = inspector.inspect(FakeProvider())
    assert "metadata" in info
    assert "download" in info
    assert "cached" in info
    assert "cached_path" in info
    assert info["cached"] is False


def test_inspect_cached():
    inspector = ModelInspector(FakeAssetManager(cached=True))
    info = inspector.inspect(FakeProvider())
    assert info["cached"] is True
    assert info["cached_path"] == "/fake/cache/path"


def test_diagnostic_report_returns_dict():
    inspector = ModelInspector(FakeAssetManager())
    diag = inspector.diagnostic_report(FakeProvider())
    assert isinstance(diag, dict)
    assert diag["model_name"] == "Fake Model"
    assert diag["cached"] is False


def test_confirm_cached_returns_true(monkeypatch):
    inspector = ModelInspector(FakeAssetManager(cached=True))
    result = inspector.confirm(FakeProvider())
    assert result is True


def test_confirm_not_cached_asks(monkeypatch):
    inspector = ModelInspector(FakeAssetManager())
    monkeypatch.setattr("builtins.input", lambda _: "s")
    result = inspector.confirm(FakeProvider())
    assert result is True


def test_confirm_not_cached_declines(monkeypatch):
    inspector = ModelInspector(FakeAssetManager())
    monkeypatch.setattr("builtins.input", lambda _: "n")
    result = inspector.confirm(FakeProvider())
    assert result is False
