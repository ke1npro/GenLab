class GenLabError(Exception):
    pass

class ConfigError(GenLabError):
    pass

class ModelError(GenLabError):
    pass

class ModelNotFoundError(ModelError):
    pass

class ModelLoadError(ModelError):
    pass

class ModelMemoryError(ModelError):
    pass

class TaskError(GenLabError):
    pass

class TaskNotSupportedError(TaskError):
    pass

class TaskValidationError(TaskError):
    pass

class PipelineError(GenLabError):
    pass

class ServiceError(GenLabError):
    pass

class HuggingFaceError(ServiceError):
    pass

class ExportError(ServiceError):
    pass

class StorageError(GenLabError):
    pass

class AssetError(GenLabError):
    pass

class DownloadError(AssetError):
    pass

class InsufficientDiskError(AssetError):
    pass
