from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genlab.core.exceptions import StorageError
from genlab.core.paths import resolve_paths
from genlab.models.manager import ModelManager
from genlab.models.registry import get_provider
from genlab.tasks.registry import get_task


class Step(ABC):
    @abstractmethod
    def execute(self, ctx: dict) -> dict:
        ...


class ResolvePathsStep(Step):
    def execute(self, ctx: dict) -> dict:
        paths = resolve_paths(ctx.get("config_dir", "configs"))
        return {"paths": paths}


class LoadModelStep(Step):
    def execute(self, ctx: dict) -> dict:
        model_name = ctx["model"]
        paths = ctx["paths"]
        mgr = ModelManager(cache_dir=paths["cache_dir"])
        provider_cls = get_provider(model_name)
        provider = provider_cls()

        artifact_path = mgr.ensure(provider.get_model_id())
        provider.load(artifact_path)

        return {"provider": provider, "manager": mgr}


class PrepareInputsStep(Step):
    def execute(self, ctx: dict) -> dict:
        task_name = ctx["task"]
        task_cls = get_task(task_name)
        task = task_cls()

        provider = ctx["provider"]
        task.validate(provider)

        kwargs = dict(ctx.get("kwargs", {}))
        kwargs.pop("overrides", None)

        overrides = dict(ctx.get("overrides", {}))
        model_overrides = overrides.pop("model", {})
        model_cfg = ctx.get("config", {}).get("model", {})

        merged = {**model_cfg, **model_overrides}
        inputs = task.prepare_inputs(**{**kwargs, **merged})
        return {"task": task, "inputs": inputs}


class GenerateStep(Step):
    def execute(self, ctx: dict) -> dict:
        provider = ctx["provider"]
        inputs = ctx["inputs"]
        outputs = provider.generate(inputs)
        return {"outputs": outputs}


class PostprocessStep(Step):
    def execute(self, ctx: dict) -> dict:
        task = ctx["task"]
        outputs = ctx["outputs"]
        result = task.postprocess(outputs)
        return {"result": result}


class ExportStep(Step):
    def execute(self, ctx: dict) -> dict:
        from genlab.services.exporter import export_video

        result = ctx["result"]
        paths = ctx["paths"]
        config = ctx.get("config", {})
        model_name = ctx["model"]
        task_name = ctx["task"]
        kwargs = ctx.get("kwargs", {})

        manifest = {
            "model": model_name,
            "task": task_name,
            "prompt": kwargs.get("prompt", ""),
            "seed": kwargs.get("seed"),
            "steps": config.get("model", {}).get("steps", 50),
            "fps": config.get("model", {}).get("fps", 8),
            "frames": config.get("model", {}).get("frames", 49),
            "guidance_scale": config.get("model", {}).get("guidance_scale", 7.0),
            "resolution": config.get("model", {}).get("resolution"),
            "gpu": ctx.get("hardware", {}).get("gpu", "N/A"),
            "profile": config.get("profile", {}).get("name", "default"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        video_path = export_video(
            frames=result.get("frames", []),
            output_dir=paths["runs_dir"],
            fps=config.get("model", {}).get("fps", 8),
            manifest=manifest,
        )
        return {"video_path": video_path, "manifest": manifest}


class CleanupStep(Step):
    def execute(self, ctx: dict) -> dict:
        provider = ctx.get("provider")
        if provider:
            provider.unload()
        return {}
