from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from genlab.tasks.base import BaseTask


_tasks: dict[str, type["BaseTask"]] = {}


def register_task(name: str):
    def decorator(cls: type["BaseTask"]) -> type["BaseTask"]:
        cls.task_id = name
        _tasks[name] = cls
        return cls
    return decorator


def get_task(name: str) -> type["BaseTask"]:
    if name not in _tasks:
        from genlab.core.exceptions import TaskError
        raise TaskError(f"Task '{name}' no registrada. Disponibles: {list(_tasks.keys())}")
    return _tasks[name]


def list_tasks() -> list[str]:
    return list(_tasks.keys())
