import pytest

from genlab.core.exceptions import ModelNotFoundError, TaskNotSupportedError
from genlab.models.base import BaseProvider
from genlab.models.manager import ModelManager
from genlab.models.registry import get_provider, list_providers, register_provider
from genlab.tasks.base import BaseTask
from genlab.tasks.registry import get_task, list_tasks, register_task


class FakeProvider(BaseProvider):
    capabilities = {"supports_text_to_video": True}

    def load(self, artifact):
        self._loaded = True

    def generate(self, inputs):
        return {"frames": [1, 2, 3]}

    def unload(self):
        self._loaded = False


def test_register_and_get_provider():
    assert "test_provider" not in list_providers()

    @register_provider("test_provider")
    class TestProvider(FakeProvider):
        pass

    assert "test_provider" in list_providers()
    cls = get_provider("test_provider")
    assert cls is TestProvider


def test_get_provider_not_found():
    with pytest.raises(ModelNotFoundError):
        get_provider("non_existent")


def test_provider_capabilities():
    p = FakeProvider()
    assert p.capabilities["supports_text_to_video"] is True


def test_model_manager_cache_dir(tmp_path):
    mgr = ModelManager(cache_dir=str(tmp_path / "cache"))
    assert (tmp_path / "cache").is_dir()


def test_model_manager_get_info_not_found(tmp_path):
    mgr = ModelManager(cache_dir=str(tmp_path / "cache"))
    info = mgr.get_info("nonexistent/model")
    assert info["exists"] is False


def test_register_and_get_task():
    @register_task("test_task")
    class TestTask(BaseTask):
        task_id = "test_task"

        def validate(self, provider):
            pass

        def prepare_inputs(self, **kwargs):
            return {}

        def postprocess(self, outputs):
            return outputs

    assert "test_task" in list_tasks()
    cls = get_task("test_task")
    assert cls is TestTask


def test_base_task_validate():
    @register_task("text_to_video")
    class RealTask(BaseTask):
        task_id = "text_to_video"

        def prepare_inputs(self, **kwargs):
            return {}

        def postprocess(self, outputs):
            return outputs

    task = RealTask()
    provider = FakeProvider()
    task.validate(provider)


def test_base_task_validate_fails():
    @register_task("image_to_video")
    class FakeTask(BaseTask):
        task_id = "image_to_video"

        def prepare_inputs(self, **kwargs):
            return {}

        def postprocess(self, outputs):
            return outputs

    task = FakeTask()
    provider = FakeProvider()
    with pytest.raises(TaskNotSupportedError):
        task.validate(provider)
