# Architecture — GenLab

## Principios

1. **Task-first**: el usuario elige una *tarea* (text_to_video) y un *modelo*; el sistema valida `provider.capabilities.supports(task)`.
2. **Colab es runtime, no arquitectura**. Todo lo específico de Colab vive tras `core/environment.py` + `config/environments/colab.yaml`.
3. **Provider ≠ Model Manager**. El Provider solo infiere; el Manager gestiona ciclo de vida de pesos.
4. **Config por precedencia**: `default < entorno (env) < modelo < perfil < args CLI`. Sin editar código para cambiar parámetros. El entorno se detecta automáticamente (Colab vs local).
5. **Contratos fijados antes de implementar**. El Pipeline define la interfaz del Provider, no al revés.
6. **Registry por decorador**. Agregar modelo = crear archivo + decorar; no editar registros centrales.
7. **Mantenibilidad > velocidad**.

## Diagrama de capas

```
┌─────────────────────────────────────────────┐
│          interfaces/  (CLI, API)             │
└───────────────────────┬─────────────────────┘
                        │ usa (no acopla)
┌───────────────────────▼─────────────────────┐
│            pipeline/  (orchestrator)         │
│   steps: resolve→load→prepare→generate→     │
│          postprocess→export→cleanup         │
└───┬───────────────┬───────────────┬─────────┘
    │               │               │
┌───▼────┐   ┌──────▼──────┐  ┌─────▼──────┐
│ tasks  │   │   models    │  │  services  │
│(intent)│   │provider+mgr │  │ hf/caching │
└───┬────┘   └──────┬──────┘  │ exporter/  │
    │               │         │ drive/     │
    │               │         │ metrics    │
    │               │         └─────┬──────┘
┌───▼───────────────▼───────────────▼─────────┐
│  config/ • core/ • storage/ • utils/         │
└─────────────────────────────────────────────┘
```

- `interfaces/` consume `pipeline/`. Nunca el pipeline consume interfaces.
- `pipeline/` orquesta `tasks` + `models` + `services`.
- `core/`, `config/`, `storage/`, `utils/` son hojas: casi nada depende de ellos salvo ellos mismos.

## Responsabilidades por módulo

| Módulo | Responsabilidad | No hace |
|---|---|---|
| `config/` | Cargar YAML, mergear precedencia (default < env < modelo < perfil < args), validar schema | Saber de Colab/modelos |
| `core/` | Bootstrap, detección HW, paths, excepciones, eventos | Lógica de inferencia |
| `models/` | `BaseProvider` (inferencia) + `ModelManager` (ciclo de vida) + registry | Descargar directo en provider |
| `tasks/` | Esquema de entrada/salida por tarea, validación | Ejecutar inferencia |
| `pipeline/` | Orquestar steps en orden | Implementar modelos |
| `services/` | HF login/descargas, caché, export, drive, métricas | Decidir qué tarea correr |
| `storage/` | Abstracción de rutas (local/drive/null) | Lógica de negocio |
| `interfaces/` | CLI / API REST | Reimplementar pipeline |

## Contratos clave

### BaseProvider (inferencia únicamente)
```
load(artifact)            # recibe pesos ya resueltos por ModelManager
generate(inputs) -> output
unload()
capabilities              # dict de supports_*
estimate_memory(task, cfg)-> dict
supports_offload() -> bool
```

### ModelManager (ciclo de vida de pesos)
```
ensure(model_id)          # descarga si falta, reusa si está (MVP)
get_info(model_id)        # ruta, tamaño, revisión
clear_cache(model_id)     # libera /content
# Beta: update(), delete(), multi-versión
```

### Task (intención + esquema)
```
TaskInput  (validado)
TaskOutput
validate(provider)        # usa provider.capabilities
```

### Pipeline steps
`resolve_paths → load_model → prepare_inputs → generate → postprocess → export → cleanup`
Cada step es reemplazable/salteable según `provider.capabilities`.

## Flujo completo

```
launcher.ipynb
  → install deps, mount Drive, git pull
  → bootstrap()  (detecta entorno + reporte diagnóstico)
  → GenLab.run(task, model, prompt, config)
        → config loader (precedencia: default → env → modelo → perfil → args)
        → TaskRegistry resuelve Task
        → ModelRegistry resuelve Provider
        → valida capabilities.supports(task)
        → pipeline orquesta steps
        → exporter guarda .mp4 + manifest.json
        → drive service sincroniza a Drive
        → metrics registra ejecución
```

## Decisiones arquitectónicas

Ver `.ai/decisions.md`. Cambios estructurales en `.ai/changelog_architecture.md`.
