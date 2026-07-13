from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenLabConfig:
    model: dict[str, Any] = field(default_factory=dict)
    profile: dict[str, Any] = field(default_factory=dict)
    hardware: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    services: dict[str, Any] = field(default_factory=dict)
    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)

    def resolve(self, *keys: str, default: Any = None) -> Any:
        value = self._raw
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default

    @classmethod
    def from_dict(cls, data: dict) -> "GenLabConfig":
        known = {"model", "profile", "hardware", "output", "services"}
        kwargs = {k: v for k, v in data.items() if k in known}
        return cls(
            **kwargs,
            _raw=data,
        )
