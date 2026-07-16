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


_PIPELINE_TO_PROVIDER: dict[str, str] = {
    "FluxPipeline": "flux",
    "StableDiffusionXLPipeline": "sdxl",
}


def detect_provider(model_id: str) -> str | None:
    try:
        from huggingface_hub import hf_hub_url
        import requests
        url = hf_hub_url(repo_id=model_id, filename="model_index.json")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        class_name = data.get("_class_name", "")
        return _PIPELINE_TO_PROVIDER.get(class_name)
    except Exception:
        return None
