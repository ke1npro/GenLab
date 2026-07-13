# Coding Rules — GenLab

Para humanos e agentes de IA. Código pequeño, bajo acoplamiento, alta cohesión.

## Convenciones generales
- Python 3.11+. Imports **absolutos** (`from genlab.core.bootstrap import bootstrap`).
- Nombres: `snake_case` funciones/vars, `PascalCase` clases, `KEBAB` en YAML.
- Tipado obligatorio en firmas públicas (`def generate(self, inp: TaskInput) -> TaskOutput`).
- Un módulo = una responsabilidad. Una función = una acción (< ~40 líneas ideal).
- Sin lógica de negocio en `notebooks/`. El notebook solo llama `bootstrap()` + `GenLab.run()`.

## Estilo
- Docstrings cortos: qué hace y por qué (no cómo).
- Errores explícitos: lanzar excepciones de `core/exceptions.py`, no `print` + `return None`.
- Logging vía `services/metrics` o logger estándar; no `print` suelto en módulos core.
- YAML es fuente de parámetros; el código lee config, no hardcodea defaults de usuario.

## Patrones
- **Registry por decorador**: `@register_provider("cogvideo")` / `@register_task("text_to_video")`.
- **Config precedencia**: `default < entorno (env) < modelo < perfil < args`. El loader resuelve, nadie más. El entorno se detecta automáticamente.
- **Contrato sobre isinstance**: nunca `if isinstance(provider, Flux)` en tasks/pipeline. Usa `capabilities`.
- **Storage abstracto**: todo path pasa por `storage/`, nunca `os.path` directo a `/content` o Drive fuera de `services/drive`.

## Reglas para nuevos Providers
1. Crear `src/genlab/models/impl/<modelo>.py`.
2. Herear `BaseProvider`. Implementar `load/generate/unload/estimate_memory`.
3. Declarar `capabilities` (dict `supports_*`).
4. Decorar `@register_provider("<modelo>")`.
5. Crear `config/models/<modelo>.yaml` con defaults.
6. El Provider **nunca** descarga: pide pesos al `ModelManager`.
7. No referenciar Colab/Drive directamente.

## Reglas para nuevas Tasks
1. Crear `src/genlab/tasks/<task>.py` con `TaskInput`, `TaskOutput`.
2. Implementar `validate(provider)` usando `provider.capabilities`.
3. Decorar `@register_task("<task>")`.
4. No ejecutar inferencia; delegar al pipeline step `generate`.
5. Documentar entradas/salidas en `docs/tasks.md`.

## Reglas para nuevos Services
1. Una responsabilidad única (HF, caché, export, drive, métricas).
2. Sin estado global mutable innecesario; recibir deps por parámetro.
3. No acoplar a un modelo específico.
4. Documentar en `docs/` o `architecture.md` si cambia flujo.

## Actualización de docs
Toda decisión importante → `decisions.md`. Cambio estructural → `changelog_architecture.md` + `architecture.md`. Nuevo provider/task → `docs/providers.md` / `docs/tasks.md`.

## Regla de lectura obligatoria (agentes de IA)
Antes de implementar cualquier tarea importante, leer SIEMPRE en orden:
1. `.ai/current_focus.md` (estado efímero del hito actual)
2. `.ai/project_context.md`
3. `.ai/architecture.md`
4. `.ai/coding_rules.md`

Al cambiar de hito, actualizar `.ai/current_focus.md` para reflejar el nuevo objetivo.

