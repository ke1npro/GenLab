from __future__ import annotations

from pathlib import Path
from typing import Any

from genlab.assets.manager import AssetManager


class ModelManager:
    def __init__(self, cache_dir: str | None = None):
        cache_dir = cache_dir or "models_cache"
        self._assets = AssetManager(cache_dir)

    def ensure(self, model_id: str) -> str:
        return self._assets.resolve_raw(model_id)

    def ensure_provider(self, provider: Any, strategy: str = "selective") -> str:
        return self._assets.resolve(provider, strategy=strategy)

    def inspect(self, provider: Any) -> dict[str, Any]:
        return self._assets.estimate(provider)

    def get_info(self, model_id: str) -> dict[str, Any]:
        path = self._assets.cached_path(model_id)
        if not path:
            return {"exists": False, "path": None, "size_mb": 0}
        total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        return {
            "exists": True,
            "path": str(path),
            "size_mb": round(total / (1024 * 1024), 1),
        }

    def clear_cache(self, model_id: str) -> None:
        self._assets.clear(model_id)

    def clear_all(self) -> None:
        self._assets.clear_all()
