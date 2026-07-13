from __future__ import annotations

import os

from genlab.core.exceptions import HuggingFaceError


def resolve_token(token: str | None = None) -> str | None:
    if token:
        return token
    token = os.environ.get("HF_TOKEN")
    if token:
        return token
    try:
        from huggingface_hub import get_token
        return get_token()
    except ImportError:
        return None
    except Exception:
        return None


def ensure_login(token: str | None = None) -> bool:
    resolved = resolve_token(token)
    if not resolved:
        raise HuggingFaceError(
            "Token de Hugging Face no encontrado. "
            "Configúralo vía HF_TOKEN env var, config YAML, o huggingface-cli login."
        )
    try:
        from huggingface_hub import login
        login(token=resolved, add_to_git_credential=False)
        return True
    except Exception as exc:
        raise HuggingFaceError(f"Error al autenticar en Hugging Face: {exc}") from exc
