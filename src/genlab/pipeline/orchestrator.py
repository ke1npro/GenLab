from __future__ import annotations

from typing import Any

from genlab.config.loader import load_config
from genlab.core.exceptions import PipelineError
from genlab.core.hardware import detect_hardware
from genlab.pipeline.steps import (
    CleanupStep,
    ExportStep,
    GenerateStep,
    InspectModelStep,
    LoadModelStep,
    PostprocessStep,
    PrepareInputsStep,
    ResolvePathsStep,
)


class Pipeline:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self._steps = [
            ("resolve_paths", ResolvePathsStep()),
            ("inspect_model", InspectModelStep()),
            ("load_model", LoadModelStep()),
            ("prepare_inputs", PrepareInputsStep()),
            ("generate", GenerateStep()),
            ("postprocess", PostprocessStep()),
            ("export", ExportStep()),
            ("cleanup", CleanupStep()),
        ]

    def run(
        self,
        task: str,
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "task": task,
            "model": model,
            "config_dir": self.config_dir,
            "kwargs": kwargs,
        }

        cfg = load_config(
            model=model,
            config_dir=self.config_dir,
        )
        ctx["config"] = cfg
        ctx["overrides"] = kwargs.get("overrides", {})

        hw = detect_hardware()
        ctx["hardware"] = hw

        for step_name, step in self._steps:
            try:
                result = step.execute(ctx)
                ctx.update(result)
            except Exception as exc:
                if "provider" in ctx and ctx["provider"]:
                    ctx["provider"].unload()
                raise PipelineError(f"Step '{step_name}' falló: {exc}") from exc

        return {
            "image_path": ctx.get("image_path"),
            "video_path": ctx.get("video_path"),
            "manifest": ctx.get("manifest"),
        }
