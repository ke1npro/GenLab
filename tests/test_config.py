from genlab.config.loader import load_config
from genlab.config.schema import GenLabConfig


def test_loads_defaults(tmp_configs):
    cfg = load_config(config_dir=tmp_configs)
    assert cfg.output["dir"] == "outputs"
    assert cfg.model["dtype"] == "float16"


def test_model_overrides_default(tmp_configs):
    cfg = load_config(model="cogvideo", config_dir=tmp_configs)
    assert cfg.model["steps"] == 50
    assert cfg.model["model_id"] == "THUDM/CogVideoX-2b"


def test_profile_overrides_model(tmp_configs):
    cfg = load_config(model="cogvideo", profile="fast", config_dir=tmp_configs)
    assert cfg.model["steps"] == 20
    assert cfg.hardware["enable_offload"] is True


def test_overrides_have_highest_precedence(tmp_configs):
    cfg = load_config(
        model="cogvideo",
        profile="fast",
        overrides={"model": {"steps": 99}},
        config_dir=tmp_configs,
    )
    assert cfg.model["steps"] == 99


def test_returns_genlab_config_instance(tmp_configs):
    cfg = load_config(config_dir=tmp_configs)
    assert isinstance(cfg, GenLabConfig)
