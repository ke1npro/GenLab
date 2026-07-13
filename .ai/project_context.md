# Project Context — GenLab

Lee esto en < 5 min para entender el proyecto.

## ¿Qué es?
Plataforma modular para correr modelos open source de IA (video/imagen/audio/LLM) en Colab, extensible a VPS/local/nube sin reescrituras. El notebook es solo un launcher.

## ¿Cómo está organizado?
```
src/genlab/
  config/      carga y validación YAML (precedencia)
  core/        bootstrap, detección HW, paths, excepciones
  models/      BaseProvider (inferencia) + ModelManager (pesos) + registry
  tasks/       una clase Task por tarea + registry
  pipeline/    orchestrator + steps (resolve→load→...→export→cleanup)
  services/    huggingface, caching, exporter, drive, metrics
  storage/     local / drive / null (abstracción de paths)
  interfaces/  cli / api (consumen pipeline)
  utils/       helpers (imagen, video, ids, timing, yaml)
notebooks/launcher.ipynb   launcher mínimo
configs/  prompts/  outputs/  docs/  .ai/
```

## Módulos clave
- **Provider**: solo inferencia (`load/generate/unload/capabilities/estimate_memory`).
- **ModelManager**: ciclo de vida de pesos (`ensure/get_info/clear_cache`).
- **Task**: intención + esquema de entrada/salida + validación vs capabilities.
- **Pipeline**: orquesta steps; es el corazón del proyecto.

## ¿Qué falta por hacer? (estado)
- MVP en diseño. Pendiente implementar hitos 1.1 → 1.8.
- Solo CogVideoX (text_to_video) planeado para MVP.
- Ningún provider real aún escrito.

## Decisiones importantes ya tomadas
1. Separación Provider / ModelManager (ver `decisions.md` D1).
2. Pipeline diseñado antes que el primer Provider (D2).
3. Config por perfiles con precedencia (D3).
4. API REST diferida a v1.0 (D4).
5. Plugins diferidos a post-v1.0 (D5).
6. Task registry mínimo (D6).
7. Manifest + captura benchmark en MVP (D7).
8. Bootstrap con reporte diagnóstico (D8).

## Antes de tocar código
Revisa siempre: `architecture.md`, `roadmap.md`, `project_context.md`, `decisions.md`.
