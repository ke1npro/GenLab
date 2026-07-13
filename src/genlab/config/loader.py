from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from genlab.config.schema import GenLabConfig


def _find_config_dir() -> Path:
    """Busca configs/ desde CWD hacia arriba o junto al paquete."""
    candidates = [
        Path.cwd() / "configs",
        Path(__file__).resolve().parent.parent.parent.parent / "configs",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(
    model: str | None = None,
    profile: str | None = None,
    overrides: dict[str, Any] | None = None,
    config_dir: str | Path | None = None,
) -> GenLabConfig:
    if config_dir is None:
        config_dir = _find_config_dir()
    config_dir = Path(config_dir)

    merged: dict[str, Any] = {}

    layers: list[tuple[str, Path]] = [
        ("default", config_dir / "default.yaml"),
    ]

    from genlab.core.environment import detect_environment
    env = detect_environment()
    env_type = env["type"]
    env_config = config_dir / "environments" / f"{env_type}.yaml"
    if env_config.is_file():
        layers.append((f"env:{env_type}", env_config))

    if model:
        layers.append((f"model:{model}", config_dir / "models" / f"{model}.yaml"))

    if profile:
        layers.append((f"profile:{profile}", config_dir / "profiles" / f"{profile}.yaml"))

    for name, path in layers:
        data = _load_yaml(path)
        merged = _deep_merge(merged, data)

    if overrides:
        merged = _deep_merge(merged, overrides)

    return GenLabConfig.from_dict(merged)
