from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from genlab.models.base import BaseProvider


_providers: dict[str, type["BaseProvider"]] = {}


def register_provider(name: str):
    def decorator(cls: type["BaseProvider"]) -> type["BaseProvider"]:
        _providers[name] = cls
        return cls
    return decorator


def get_provider(name: str) -> type["BaseProvider"]:
    if name not in _providers:
        from genlab.core.exceptions import ModelNotFoundError
        raise ModelNotFoundError(f"Provider '{name}' no registrado. Disponibles: {list(_providers.keys())}")
    return _providers[name]


def list_providers() -> list[str]:
    return list(_providers.keys())


_PIPELINE_INFO: dict[str, dict[str, str | None]] = {
    "FluxPipeline": {"provider": "flux", "task": "text_to_image"},
    "StableDiffusionXLPipeline": {"provider": "sdxl", "task": "text_to_image"},
    "StableDiffusionPipeline": {"provider": None, "task": "text_to_image"},
    "WanPipeline": {"provider": "wan", "task": "text_to_video"},
    "CogVideoXPipeline": {"provider": "cogvideo", "task": "text_to_video"},
    "PixArtSigmaPipeline": {"provider": None, "task": "text_to_image"},
    "LatentConsistencyModelPipeline": {"provider": None, "task": "text_to_image"},
    "AnimateDiffPipeline": {"provider": None, "task": "text_to_video"},
    "I2VGenXLPipeline": {"provider": None, "task": "text_to_video"},
    "StableVideoDiffusionPipeline": {"provider": None, "task": "text_to_video"},
    "TextToVideoSDPipeline": {"provider": None, "task": "text_to_video"},
}


def detect_model(model_id: str) -> dict[str, str | None] | None:
    try:
        from huggingface_hub import hf_hub_url
        import requests
        url = hf_hub_url(repo_id=model_id, filename="model_index.json")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        class_name = data.get("_class_name", "")
        info = _PIPELINE_INFO.get(class_name)
        if info:
            return info
        if "Video" in class_name or "video" in class_name:
            return {"provider": None, "task": "text_to_video"}
        return {"provider": None, "task": "text_to_image"}
    except Exception:
        return None


def detect_provider(model_id: str) -> str | None:
    info = detect_model(model_id)
    return info.get("provider") if info else None
