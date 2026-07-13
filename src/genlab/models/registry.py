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
