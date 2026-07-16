from genlab.models.base import BaseProvider
from genlab.models.manager import ModelManager
from genlab.models.registry import register_provider, get_provider, list_providers, detect_provider

# Registrar providers built-in
from genlab.models.impl import cogvideo  # noqa: F401
from genlab.models.impl import wan  # noqa: F401
from genlab.models.impl import flux  # noqa: F401
from genlab.models.impl import sdxl  # noqa: F401
from genlab.models.impl import ssd1b  # noqa: F401

__all__ = ["BaseProvider", "ModelManager", "register_provider", "get_provider", "list_providers", "detect_provider"]
