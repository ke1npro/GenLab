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

## 2026-07-13 — Optimización de descargas HF + generación de imágenes

- **AssetManager refactorizado**: `snapshot_download` con `max_workers=8` (descarga paralela), `hf_transfer` automático para descargas >500 MB, verificación de espacio libre, sonda de ancho de banda con caché, método `diagnostic()` con reporte completo.
- **ModelInspector mejorado**: nuevo `diagnostic_report()` con formato (modelo, repo, descarga estimada, espacio libre, hf_transfer, tiempo estimado). Menú de estrategia de descarga (1: selectivo, 2: completo). Estrategia propagada vía `ctx["_strategy"]`.
- **Providers**: eliminados args deprecados (`resume_download`, `local_dir_use_symlinks`). `BaseProvider` ahora acepta `config` opcional y `get_model_id()` lee desde config con fallback a `_default_model_id`.
- **Nuevos providers**: `flux` (FLUX.1-schnell, `FluxPipeline`, `text_to_image`) y `sdxl` (SDXL 1.0, `StableDiffusionXLPipeline`, `text_to_image`).
- **Nueva task**: `text_to_image` con prepare_inputs/postprocess.
- **Pipeline**: `ExportStep` ahora detecta tipo de salida (image → PNG, frames → MP4). `_cfg_to_dict()` aplicado en todos los steps para evitar `GenLabConfig.get()`.
- **Notebook**: menú interactivo numerado con 4 modelos + model_id personalizable + detección automática de tarea.
- **FLUX fix**: agregados `text_encoder_2/*` y `tokenizer_2/*` a patrones requeridos (FLUX usa T5 como segundo text encoder).
- **Docs actualizados**: providers.md, tasks.md, pipeline.md, bootstrap.md, current_focus.md, changelog_architecture.md.

## 2026-07-13 — Fundación documental y arquitectura inicial
- Se define la arquitectura task-first por capas. Creación de todos los documentos .ai/ y docs/.

## 2026-07-13 — Separación Provider / Model Manager (D1)
## 2026-07-13 — Pipeline adelantado (D2)
## 2026-07-13 — API y Plugins diferidos (D4, D5)
## 2026-07-13 — current_focus.md como punto de entrada de agentes
