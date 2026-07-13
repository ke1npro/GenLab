# Pipeline — GenLab

Flujo completo desde `launcher.ipynb` hasta el video exportado.

## Entrada
```python
GenLab().run(
    task="text_to_video",
    model="cogvideo",
    prompt="...",
    config={'model': {'steps': 50, 'fps': 8, 'frames': 49}},
)
```
El parámetro `config` acepta cualquier clave de la jerarquía YAML (model, hardware, etc.).  
El namespace `model` se aplana automáticamente en `PrepareInputsStep` para pasarlo a `task.prepare_inputs()`.

## Steps (implementados en `pipeline/steps.py`)

```
1. resolve_paths → storage resuelve rutas (local/drive) según entorno
2. load_model    → ModelManager.ensure(model) + Provider.load(artifact)
3. prepare_inputs → Task valida provider; prepara inputs según task
4. generate      → Provider.generate(inputs) -> outputs
5. postprocess   → Task.postprocess(outputs) -> frames listos
6. export        → exporter guarda .mp4 + manifest.json en outputs/
7. cleanup       → provider.unload(); liberar VRAM
```

## Contexto del pipeline
Cada step recibe y modifica un diccionario `ctx` compartido:
- `ctx["task"]`, `ctx["model"]` — parámetros de entrada
- `ctx["config"]` — configuración mergeada
- `ctx["paths"]` — rutas resueltas por entorno
- `ctx["provider"]` — instancia del provider (cargado en step 2)
- `ctx["task"]` — instancia de la tarea
- `ctx["inputs"]` — inputs preparados
- `ctx["outputs"]` — salida raw del provider
- `ctx["result"]` — salida postprocesada
- `ctx["video_path"]`, `ctx["manifest"]` — resultado final

## Manifest (junto al video)
```json
{
  "model": "cogvideo",
  "task": "text_to_video",
  "prompt": "...",
  "seed": 12345,
  "steps": 50,
  "fps": 8,
  "frames": 49,
  "guidance_scale": 7.0,
  "resolution": {"width": 480, "height": 720},
  "gpu": "Tesla T4",
  "profile": "balanced",
  "timestamp": "2026-07-13T..."
}
```

## Validación temprana
Antes de `load_model`: `task.validate(provider)` usando `provider.capabilities`.
Si no soporta la tarea → `TaskNotSupportedError` claro, sin cargar pesos.

## Notas
- Cada step es reemplazable/salteable según `provider.capabilities`.
- El orchestrator es agnóstico de interfaz (CLI/API/notebook lo consumen igual).
- Diseñado antes que el primer Provider (decisión D2).
