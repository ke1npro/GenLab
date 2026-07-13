from pathlib import Path

import yaml

from genlab.config.loader import load_config


def test_environment_config_loaded_when_present(tmp_path):
    conf = tmp_path / "configs"
    conf.mkdir()
    (conf / "default.yaml").write_text(yaml.dump({
        "output": {"dir": "outputs"},
        "model": {"dtype": "float16"},
    }))

    env_dir = conf / "environments"
    env_dir.mkdir()
    (env_dir / "local.yaml").write_text(yaml.dump({
        "hardware": {"enable_offload": False},
    }))

    cfg = load_config(config_dir=conf)
    assert cfg.hardware["enable_offload"] is False


def test_environment_config_not_required(tmp_path):
    conf = tmp_path / "configs"
    conf.mkdir()
    (conf / "default.yaml").write_text(yaml.dump({
        "output": {"dir": "outputs"},
    }))

    cfg = load_config(config_dir=conf)
    assert cfg.output["dir"] == "outputs"
