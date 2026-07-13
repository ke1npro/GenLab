from pathlib import Path

import pytest
import yaml


@pytest.fixture
def tmp_configs(tmp_path: Path) -> Path:
    conf = tmp_path / "configs"
    conf.mkdir()

    (conf / "default.yaml").write_text(yaml.dump({
        "output": {"dir": "outputs", "manifest": True},
        "model": {"dtype": "float16", "seed": None},
        "hardware": {"enable_offload": False},
        "services": {"huggingface": {"token": None}},
    }))

    (conf / "models").mkdir()
    (conf / "models" / "cogvideo.yaml").write_text(yaml.dump({
        "model": {
            "model_id": "THUDM/CogVideoX-2b",
            "steps": 50,
            "guidance_scale": 7.0,
            "fps": 8,
            "frames": 49,
            "resolution": {"width": 480, "height": 720},
        },
    }))

    (conf / "profiles").mkdir()
    (conf / "profiles" / "balanced.yaml").write_text(yaml.dump({
        "model": {"dtype": "float16", "steps": 50},
        "hardware": {"enable_offload": False, "enable_amp": False},
    }))

    (conf / "profiles" / "fast.yaml").write_text(yaml.dump({
        "model": {"steps": 20, "dtype": "int8"},
        "hardware": {"enable_offload": True},
    }))

    return conf
