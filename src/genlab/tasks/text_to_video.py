from __future__ import annotations

from typing import Any

from genlab.tasks.base import BaseTask
from genlab.tasks.registry import register_task


@register_task("text_to_video")
class TextToVideoTask(BaseTask):
    task_id = "text_to_video"

    def prepare_inputs(self, **kwargs) -> dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt")
        seed = kwargs.get("seed")
        steps = kwargs.get("steps", 50)
        frames = kwargs.get("frames", 49)
        fps = kwargs.get("fps", 8)
        resolution = kwargs.get("resolution", {"width": 480, "height": 720})
        guidance_scale = kwargs.get("guidance_scale", 7.0)

        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_inference_steps": steps,
            "num_frames": frames,
            "fps": fps,
            "width": resolution.get("width", 480),
            "height": resolution.get("height", 720),
            "guidance_scale": guidance_scale,
        }

    def postprocess(self, outputs: dict[str, Any]) -> dict[str, Any]:
        frames = outputs.get("frames", [])
        return {
            "frames": frames,
            "video_path": outputs.get("video_path"),
            "manifest": outputs.get("manifest", {}),
        }
