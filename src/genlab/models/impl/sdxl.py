from __future__ import annotations

from typing import Any

from genlab.core.exceptions import ModelLoadError
from genlab.models.base import BaseProvider
from genlab.models.registry import register_provider


@register_provider("sdxl")
class SDXLProvider(BaseProvider):
    _default_model_id = "stabilityai/stable-diffusion-xl-base-1.0"
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
            "estimated_vram_gb": 8,
            "license": "openrail-m",
            "hardware_compatibility": {"t4": True},
            "description": "Stable Diffusion XL 1.0 (Stability AI) — text-to-image, 1024x1024",
        }

    def load(self, artifact: str) -> None:
        import gc
        import torch
        self.unload()
        try:
            from diffusers import StableDiffusionXLPipeline

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if self._device == "cuda" else torch.float32
            self._pipeline = StableDiffusionXLPipeline.from_pretrained(
                artifact,
                torch_dtype=dtype,
            )
            if self._device == "cuda":
                self._pipeline.to(self._device)
                for _, comp in self._pipeline.components.items():
                    if hasattr(comp, 'parameters'):
                        try:
                            comp.to(self._device)
                        except Exception:
                            pass
                self._pipeline.enable_attention_slicing()
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception as exc:
            raise ModelLoadError(f"Error al cargar SDXL desde {artifact}: {exc}") from exc

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
        import gc
        import torch
        if self._pipeline is not None:
            self._pipeline = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

    def supports_offload(self) -> bool:
        return True
