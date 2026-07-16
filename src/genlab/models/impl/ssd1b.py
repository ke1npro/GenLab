from __future__ import annotations

from typing import Any

from genlab.core.exceptions import ModelLoadError
from genlab.models.base import BaseProvider
from genlab.models.registry import register_provider


@register_provider("ssd1b")
class SSD1BProvider(BaseProvider):
    _default_model_id = "segmind/SSD-1B"
    capabilities = {
        "supports_text_to_image": True,
    }

    def __init__(self, config: dict | None = None):
        super().__init__(config=config)
        self._pipeline = None

    def get_required_files(self) -> list[str]:
        return [
            "model_index.json",
            "scheduler/*",
            "text_encoder/*",
            "text_encoder_2/*",
            "tokenizer/*",
            "tokenizer_2/*",
            "unet/*",
            "vae/*",
        ]

    def get_metadata(self) -> dict:
        return {
            "model_id": self.get_model_id(),
            "estimated_vram_gb": 3,
            "license": "openrail-m",
            "hardware_compatibility": {"t4": True},
            "description": "Segmind SSD-1B — SDXL destilado, 1.3B params, ~3GB",
        }

    def load(self, artifact: str) -> None:
        import torch
        try:
            from diffusers import StableDiffusionXLPipeline

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if self._device == "cuda" else torch.float32
            self._pipeline = StableDiffusionXLPipeline.from_pretrained(
                artifact,
                torch_dtype=dtype,
            )
            self._pipeline.to(self._device)
            if self._device == "cuda":
                self._pipeline.enable_attention_slicing()
        except Exception as exc:
            raise ModelLoadError(f"Error al cargar SSD-1B desde {artifact}: {exc}") from exc

    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        import torch
        if self._pipeline is None:
            raise ModelLoadError("Provider no cargado. Llama a load() primero.")

        prompt = inputs.get("prompt", "")
        negative_prompt = inputs.get("negative_prompt")
        num_inference_steps = inputs.get("num_inference_steps", 50)
        guidance_scale = inputs.get("guidance_scale", 7.0)
        width = inputs.get("width", 1024)
        height = inputs.get("height", 1024)
        seed = inputs.get("seed")

        generator = None
        if seed is not None:
            device = self._device or "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(seed)

        kwargs = dict(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            generator=generator,
        )
        if negative_prompt:
            kwargs["negative_prompt"] = negative_prompt

        output = self._pipeline(**kwargs)
        return {"image": output.images[0]}

    def unload(self) -> None:
        import torch
        if self._pipeline is not None:
            self._pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def supports_offload(self) -> bool:
        return True
