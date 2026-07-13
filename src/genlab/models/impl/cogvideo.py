from __future__ import annotations

from typing import Any

import torch

from genlab.core.exceptions import ModelLoadError
from genlab.models.base import BaseProvider
from genlab.models.registry import register_provider


@register_provider("cogvideo")
class CogVideoProvider(BaseProvider):
    capabilities = {
        "supports_text_to_video": True,
        "supports_image_to_video": True,
    }

    def __init__(self):
        self._pipeline = None
        self._device = None

    def get_model_id(self) -> str:
        return "THUDM/CogVideoX-2b"

    def load(self, artifact: str) -> None:
        try:
            from diffusers import CogVideoXPipeline

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if self._device == "cuda" else torch.float32
            self._pipeline = CogVideoXPipeline.from_pretrained(
                artifact,
                torch_dtype=dtype,
            )
            if self._device == "cuda":
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline.to(self._device)
        except Exception as exc:
            raise ModelLoadError(f"Error al cargar CogVideoX desde {artifact}: {exc}") from exc

    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if self._pipeline is None:
            raise ModelLoadError("Provider no cargado. Llama a load() primero.")

        prompt = inputs.get("prompt", "")
        negative_prompt = inputs.get("negative_prompt")
        num_inference_steps = inputs.get("num_inference_steps", 50)
        num_frames = inputs.get("num_frames", 49)
        guidance_scale = inputs.get("guidance_scale", 7.0)
        width = inputs.get("width", 480)
        height = inputs.get("height", 720)
        seed = inputs.get("seed")

        generator = None
        if seed is not None:
            generator = torch.Generator(device=self._device).manual_seed(seed)

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
        if self._pipeline is not None:
            self._pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def supports_offload(self) -> bool:
        return True
