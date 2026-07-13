# GenLab

Plataforma modular para ejecutar modelos open source de IA (video, imagen, audio, LLM) principalmente en **Google Colab**, diseñada para crecer sin reescrituras.

## Cómo empezar (Colab)

1. Abre `notebooks/launcher.ipynb`.
2. Ejecuta todas las celdas: instala deps, monta Drive, actualiza repo, `bootstrap()`, `GenLab.run(...)`.
3. Escribe un prompt → obtienes un `.mp4` en Drive.

## Filosofía

- Colab es **solo** entorno de ejecución. Toda la lógica vive en `src/genlab/` (Python normal).
- El notebook es un *launcher* mínimo.
- Arquitectura **task-first**: eliges tarea + modelo, el sistema valida compatibilidad.
- Mantenibilidad y modularidad > velocidad de implementación.

## Documentación (fuente de verdad)

Lee esto **antes** del código:

- `.ai/architecture.md` — arquitectura, responsabilidades, flujo, decisiones.
- `.ai/roadmap.md` — MVP → Beta → v1.0 → Future.
- `.ai/project_context.md` — resumen rápido del proyecto.
- `.ai/coding_rules.md` — convenciones y reglas para providers/tasks/services.
- `.ai/decisions.md` — decisiones importantes y su justificación.
- `.ai/changelog_architecture.md` — historial de cambios estructurales.
- `docs/providers.md` — estado y capacidades de cada modelo.
- `docs/tasks.md` — tareas soportadas, entradas/salidas.
- `docs/bootstrap.md` — qué hace `bootstrap()`.
- `docs/pipeline.md` — flujo completo launcher → video exportado.

## Estado actual

MVP en diseño. Ver `.ai/roadmap.md` y `.ai/project_context.md`.


## Para asistentes de IA

Antes de analizar el código, lee en este orden:

1. .ai/project_context.md
2. .ai/architecture.md
3. .ai/roadmap.md
4. .ai/coding_rules.md
5. docs/

Estos documentos son la fuente de verdad del proyecto.