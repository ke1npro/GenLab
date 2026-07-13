from __future__ import annotations

from pathlib import Path
from typing import Any


class LocalStorage:
    def __init__(self, base_path: str):
        self._base = Path(base_path)

    def resolve(self, *parts: str) -> str:
        return str(self._base.joinpath(*parts))

    def ensure(self, *parts: str) -> str:
        path = self._base.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    def output_dir(self) -> str:
        return self.ensure("outputs")

    def temp_dir(self) -> str:
        return self.ensure("outputs", "tmp")

    def cache_dir(self) -> str:
        return self.ensure("models_cache")
