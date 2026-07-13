from __future__ import annotations

from typing import Any

from genlab.core.exceptions import ModelLoadError
from genlab.models.base import BaseProvider
from genlab.models.registry import register_provider


@register_provider("ltx")
class LTXVideoProvider(BaseProvider):
    capabilities = {
        "supports_text_to_video": True,
    }

    def __init__(self):
        self._pipeline = None

    def get_model_id(self) -> str:
        return "Lightricks/LTX-Video"

    def load(self, artifact: str) -> None:
        import torch
        try:
            from diffusers import LTXPipeline

            self._pipeline = LTXPipeline.from_pretrained(
                artifact,
                torch_dtype=torch.bfloat16,
            )
            if torch.cuda.is_available():
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline.to("cpu")
        except Exception as exc:
            raise ModelLoadError(f"Error al cargar LTX-Video desde {artifact}: {exc}") from exc

    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        import torch
        if self._pipeline is None:
            raise ModelLoadError("Provider no cargado. Llama a load() primero.")

        prompt = inputs.get("prompt", "")
        negative_prompt = inputs.get("negative_prompt")
        num_inference_steps = inputs.get("num_inference_steps", 30)
        num_frames = inputs.get("num_frames", 121)
        guidance_scale = inputs.get("guidance_scale", 5.0)
        width = inputs.get("width", 768)
        height = inputs.get("height", 512)
        seed = inputs.get("seed")

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cuda" if torch.cuda.is_available() else "cpu").manual_seed(seed)

        output = self._pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            generator=generator,
        )
        return {"frames": output.frames[0]}

    def unload(self) -> None:
        import torch
        if self._pipeline is not None:
            self._pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def supports_offload(self) -> bool:
        return True
