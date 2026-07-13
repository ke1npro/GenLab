from __future__ import annotations

from pathlib import Path
from typing import Any

from genlab.core.exceptions import AssetError


class AssetManager:
    def __init__(self, cache_dir: str):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def resolve(self, provider: Any) -> str:
        return self._download(
            repo_id=provider.get_model_id(),
            patterns=provider.get_required_files(),
        )

    def resolve_raw(self, repo_id: str) -> str:
        return self._download(repo_id=repo_id, patterns=None)

    def _download(self, repo_id: str, patterns: list[str] | None) -> str:
        from huggingface_hub import snapshot_download

        target = self._cache_dir / repo_id.replace("/", "__")
        target.mkdir(parents=True, exist_ok=True)
        kwargs = dict(
            repo_id=repo_id,
            local_dir=str(target),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        if patterns is not None:
            kwargs["allow_patterns"] = patterns
        snapshot_download(**kwargs)
        return str(target)

    def estimate(self, provider: Any) -> dict[str, Any]:
        repo_id = provider.get_model_id()
        patterns = provider.get_required_files()

        from fnmatch import fnmatch
        from huggingface_hub import HfApi

        api = HfApi()
        info = api.model_info(repo_id, files_metadata=True)
        matched = []
        total_bytes = 0
        for s in info.siblings:
            if any(fnmatch(s.rfilename, p) for p in patterns):
                matched.append({
                    "path": s.rfilename,
                    "size_gb": round(s.size / (1024**3), 2) if s.size else 0,
                })
                total_bytes += s.size or 0

        return {
            "repo_id": repo_id,
            "files": matched,
            "total_gb": round(total_bytes / (1024**3), 2),
            "file_count": len(matched),
        }

    def cached_path(self, model_id: str) -> Path | None:
        target = self._cache_dir / model_id.replace("/", "__")
        return target if target.is_dir() else None

    def clear(self, model_id: str) -> None:
        import shutil
        target = self._cache_dir / model_id.replace("/", "__")
        if target.is_dir():
            shutil.rmtree(str(target))

    def clear_all(self) -> None:
        import shutil
        for item in self._cache_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(str(item))
