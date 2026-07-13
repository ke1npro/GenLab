from __future__ import annotations

from typing import Any

from genlab.config.loader import load_config
from genlab.core.bootstrap import bootstrap
from genlab.core.exceptions import GenLabError
from genlab.pipeline.orchestrator import Pipeline


class GenLab:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self._pipeline = Pipeline(config_dir=config_dir)

    @staticmethod
    def bootstrap(config_dir: str = "configs") -> dict:
        return bootstrap(config_dir=config_dir)

    def run(
        self,
        task: str,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        overrides = {}
        config_override = kwargs.get("config")
        if config_override:
            if isinstance(config_override, dict):
                overrides = config_override

        result = self._pipeline.run(
            task=task,
            model=model,
            prompt=prompt,
            overrides=overrides,
            **{k: v for k, v in kwargs.items() if k != "config"},
        )
        return result


def run(
    task: str,
    model: str,
    prompt: str,
    **kwargs: Any,
) -> dict[str, Any]:
    app = GenLab()
    return app.run(task=task, model=model, prompt=prompt, **kwargs)
