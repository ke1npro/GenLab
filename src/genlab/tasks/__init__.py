from genlab.tasks.base import BaseTask
from genlab.tasks.registry import register_task, get_task, list_tasks

# Registrar tasks built-in
from genlab.tasks import text_to_video  # noqa: F401

__all__ = ["BaseTask", "register_task", "get_task", "list_tasks"]
