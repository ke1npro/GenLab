from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any


class ModelManager:
    def __init__(self, cache_dir: str | None = None):
        self._cache_dir = Path(cache_dir) if cache_dir else Path("models_cache")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def ensure(self, model_id: str) -> str:
        from huggingface_hub import snapshot_download

        target = self._cache_dir / model_id.replace("/", "__")
        if target.is_dir():
            return str(target)

        target.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=model_id,
            local_dir=str(target),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        return str(target)

    def get_info(self, model_id: str) -> dict[str, Any]:
        target = self._cache_dir / model_id.replace("/", "__")
        if not target.is_dir():
            return {"exists": False, "path": None, "size_mb": 0}
        total = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
        return {
            "exists": True,
            "path": str(target),
            "size_mb": round(total / (1024 * 1024), 1),
        }

    def clear_cache(self, model_id: str) -> None:
        target = self._cache_dir / model_id.replace("/", "__")
        if target.is_dir():
            shutil.rmtree(str(target))

    def clear_all(self) -> None:
        if self._cache_dir.is_dir():
            for item in self._cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(str(item))
