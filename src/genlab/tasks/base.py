from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from genlab.models.base import BaseProvider


class BaseTask(ABC):
    task_id: str = ""

    def validate(self, provider: BaseProvider) -> None:
        capability = f"supports_{self.task_id}"
        if not provider.capabilities.get(capability, False):
            from genlab.core.exceptions import TaskNotSupportedError
            raise TaskNotSupportedError(
                f"Provider '{provider.__class__.__name__}' no soporta la tarea '{self.task_id}'"
            )

    @abstractmethod
    def prepare_inputs(self, **kwargs) -> dict[str, Any]:
        ...

    @abstractmethod
    def postprocess(self, outputs: dict[str, Any]) -> dict[str, Any]:
        ...
