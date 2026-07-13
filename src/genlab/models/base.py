from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    capabilities: dict[str, bool] = {}

    @abstractmethod
    def load(self, artifact: str) -> None:
        ...

    @abstractmethod
    def generate(self, inputs: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def unload(self) -> None:
        ...

    def estimate_memory(self, task: str, cfg: dict) -> dict[str, Any]:
        return {"estimated_gb": 0, "dtype": "float16", "offload": False}

    def supports_offload(self) -> bool:
        return False
