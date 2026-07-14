from __future__ import annotations

from typing import Any

from genlab.tasks.base import BaseTask
from genlab.tasks.registry import register_task


@register_task("text_to_image")
class TextToImageTask(BaseTask):
    task_id = "text_to_image"

    def prepare_inputs(self, **kwargs) -> dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt")
        seed = kwargs.get("seed")
        steps = kwargs.get("steps", 50)
        guidance_scale = kwargs.get("guidance_scale", 7.0)
        resolution = kwargs.get("resolution", {"width": 1024, "height": 1024})

        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
            "width": resolution.get("width", 1024),
            "height": resolution.get("height", 1024),
        }

    def postprocess(self, outputs: dict[str, Any]) -> dict[str, Any]:
        return {
            "image": outputs.get("image"),
            "manifest": outputs.get("manifest", {}),
        }
