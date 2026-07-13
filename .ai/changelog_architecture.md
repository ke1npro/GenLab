# Changelog Arquitectónico — GenLab

Historial de cambios que afectan la **estructura** del proyecto. No es changelog de código.

---

## 2026-07-13 — Code review pre-Colab: fixes y mejoras

- **Circular import eliminado**: `config/loader.py` usa import diferido de `core.environment.detect_environment` para romper el ciclo `__init__ → loader → environment → core.__init__ → bootstrap → loader`.
- **Precedencia de configuración ampliada**: ahora `default < entorno (env) < modelo < perfil < args`. El loader carga automáticamente `environments/{colab,local}.yaml` según entorno detectado.
- **PrepareInputsStep mejorado**: aplanamiento correcto de overrides (`config={'model': {'steps': 50}}`) — el namespace `model` se extrae y se mergea con la config del modelo antes de pasarlo a `task.prepare_inputs()`.
- **CogVideoProvider**: se separa `enable_model_cpu_offload()` (GPU) de `to(device)` (CPU) para evitar conflicto.
- **pyproject.toml reestructurado**: dependencias pesadas (torch, diffusers, transformers, etc.) movidas a `[project.optional-dependencies] gpu` y `video`. Core mínimo: `pyyaml`, `psutil`.
- **Notebook más robusta**: variable `REPO_URL` editable, manejo de `SecretNotFoundError` y fallback a input manual de HF token.
- **Bootstrap**: `import os` movido a nivel de módulo.
- **Exporter**: sin cambios funcionales, solo se validó que `imageio` maneja PIL Images vía `np.asarray()` interno.

## 2026-07-13 — MVP completo implementado (hitos 1.1–1.8)
- **Contenido**: Sistema de configuración, core (bootstrap, HW, paths, excepciones), models (BaseProvider, ModelManager, registry), tasks (BaseTask, text_to_video), pipeline (orchestrator + 7 steps), provider CogVideoX, servicios (HF, exporter), storage, launcher notebook, tests (28 tests).

## 2026-07-13 — Fundación documental y arquitectura inicial
- Se define la arquitectura task-first por capas. Creación de todos los documentos .ai/ y docs/.

## 2026-07-13 — Separación Provider / Model Manager (D1)
## 2026-07-13 — Pipeline adelantado (D2)
## 2026-07-13 — API y Plugins diferidos (D4, D5)
## 2026-07-13 — current_focus.md como punto de entrada de agentes
