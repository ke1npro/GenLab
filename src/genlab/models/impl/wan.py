from __future__ import annotations

from typing import Any

from genlab.core.exceptions import ModelLoadError
from genlab.models.base import BaseProvider
from genlab.models.registry import register_provider


@register_provider("wan")
class WanT2VProvider(BaseProvider):
    capabilities = {
        "supports_text_to_video": True,
    }

    def __init__(self):
        self._pipeline = None

    def get_model_id(self) -> str:
        return "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"

    def get_required_files(self) -> list[str]:
        return [
            "model_index.json",
            "scheduler/*",
            "text_encoder/*",
            "tokenizer/*",
            "transformer/*",
            "vae/*",
        ]

    def get_metadata(self) -> dict:
        return {
            "model_id": self.get_model_id(),
            "estimated_vram_gb": 11,
            "license": "apache-2.0",
            "hardware_compatibility": {"t4": True},
            "description": "Wan2.1 Text-to-Video 1.3B (Alibaba) — 480p nativo, ~5-7GB descarga",
        }

    def load(self, artifact: str) -> None:
        import torch
        try:
            from diffusers import WanPipeline

            self._pipeline = WanPipeline.from_pretrained(
                artifact,
                torch_dtype=torch.bfloat16,
            )
            if torch.cuda.is_available():
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline.to("cpu")
        except Exception as exc:
            raise ModelLoadError(f"Error al cargar Wan2.1-T2V-1.3B desde {artifact}: {exc}") from exc

    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        import torch
        if self._pipeline is None:
            raise ModelLoadError("Provider no cargado. Llama a load() primero.")

        prompt = inputs.get("prompt", "")
        num_inference_steps = inputs.get("num_inference_steps", 50)
        num_frames = inputs.get("num_frames", 81)
        guidance_scale = inputs.get("guidance_scale", 5.0)
        width = inputs.get("width", 832)
        height = inputs.get("height", 480)
        seed = inputs.get("seed")

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cuda" if torch.cuda.is_available() else "cpu").manual_seed(seed)

        output = self._pipeline(
            prompt=prompt,
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
