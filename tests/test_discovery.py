import genlab
from genlab.models import list_providers
from genlab.tasks import list_tasks


def test_cogvideo_provider_registered():
    import genlab.models.impl.cogvideo  # noqa: F401
    assert "cogvideo" in list_providers()


def test_wan_provider_registered():
    import genlab.models.impl.wan  # noqa: F401
    assert "wan" in list_providers()


def test_flux_provider_registered():
    import genlab.models.impl.flux  # noqa: F401
    assert "flux" in list_providers()


def test_sdxl_provider_registered():
    import genlab.models.impl.sdxl  # noqa: F401
    assert "sdxl" in list_providers()


def test_text_to_video_task_registered():
    import genlab.tasks.text_to_video  # noqa: F401
    assert "text_to_video" in list_tasks()


def test_text_to_image_task_registered():
    import genlab.tasks.text_to_image  # noqa: F401
    assert "text_to_image" in list_tasks()


def test_genlab_import_triggers_registration():
    import genlab
    assert "cogvideo" in list_providers()
    assert "wan" in list_providers()
    assert "flux" in list_providers()
    assert "sdxl" in list_providers()
    assert "text_to_video" in list_tasks()
    assert "text_to_image" in list_tasks()
