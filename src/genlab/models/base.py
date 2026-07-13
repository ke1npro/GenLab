from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    capabilities: dict[str, bool] = {}
    _default_model_id: str = ""

    def __init__(self, config: dict | None = None):
        self._config = config or {}

    @abstractmethod
    def load(self, artifact: str) -> None:
        ...

    @abstractmethod
    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def unload(self) -> None:
        ...

    def get_model_id(self) -> str:
        cfg_model = (self._config.get("model") or {}) if self._config else {}
        return cfg_model.get("model_id", self._default_model_id)

    def get_required_files(self) -> list[str]:
        return ["model_index.json", "scheduler/*", "text_encoder/*", "tokenizer/*", "transformer/*", "vae/*"]

    def get_metadata(self) -> dict[str, Any]:
        return {
            "model_id": self.get_model_id(),
            "estimated_vram_gb": None,
            "license": "unknown",
            "hardware_compatibility": {},
            "description": "",
        }

    def estimate_memory(self, task: str, cfg: dict) -> dict[str, Any]:
        return {"estimated_gb": 0, "dtype": "float16", "offload": False}

    def supports_offload(self) -> bool:
        return False
