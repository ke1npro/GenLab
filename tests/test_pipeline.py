from pathlib import Path

import pytest

from genlab.pipeline.steps import ResolvePathsStep


class FakeProvider:
    capabilities = {"supports_text_to_video": True}

    def load(self, artifact):
        self._loaded = True

    def generate(self, inputs):
        return {"frames": [1, 2, 3]}

    def unload(self):
        self._loaded = False


def test_resolve_paths_step(tmp_configs):
    step = ResolvePathsStep()
    ctx = {"config_dir": str(tmp_configs)}
    result = step.execute(ctx)
    assert "paths" in result
    assert "output_dir" in result["paths"]
    assert "cache_dir" in result["paths"]


def test_pipeline_import():
    from genlab.pipeline.orchestrator import Pipeline
    p = Pipeline()
    assert p is not None
