# Pipeline — GenLab

Flujo completo desde `launcher.ipynb` hasta el video exportado.

## Entrada
```python
GenLab().run(
    task="text_to_video",
    model="wan",
    prompt="...",
    config={'model': {'steps': 50, 'fps': 16, 'frames': 81}},
)
```
El parámetro `config` acepta cualquier clave de la jerarquía YAML (model, hardware, etc.).  
El namespace `model` se aplana automáticamente en `PrepareInputsStep` para pasarlo a `task.prepare_inputs()`.

## Steps (implementados en `pipeline/steps.py`)

```
1. resolve_paths  → storage resuelve rutas (local/drive) según entorno
2. inspect_model  → ModelInspector muestra metadatos del modelo y pide confirmación
3. load_model     → AssetManager.resolve(provider) descarga solo archivos necesarios + Provider.load()
4. prepare_inputs → Task valida provider; prepara inputs según task
5. generate       → Provider.generate(inputs) -> outputs
6. postprocess    → Task.postprocess(outputs) -> frames listos
7. export         → exporter guarda .mp4 + manifest.json en outputs/
8. cleanup        → provider.unload(); liberar VRAM
```

**AssetManager** usa `snapshot_download` con `allow_patterns` para descargar únicamente los archivos que coinciden con `provider.get_required_files()`. Esto evita descargar repositorios completos con variantes innecesarias (ej. LTX-Video con 111GB de modelos 13B).

## Contexto del pipeline
Cada step recibe y modifica un diccionario `ctx` compartido:
- `ctx["task"]`, `ctx["model"]` — parámetros de entrada
- `ctx["config"]` — configuración mergeada
- `ctx["paths"]` — rutas resueltas por entorno
- `ctx["_provider"]` — instancia del provider (creada en inspect, cargada en load)
- `ctx["provider"]` — provider listo para generar
- `ctx["task"]` — instancia de la tarea
- `ctx["inputs"]` — inputs preparados
- `ctx["outputs"]` — salida raw del provider
- `ctx["result"]` — salida postprocesada
- `ctx["video_path"]`, `ctx["manifest"]` — resultado final

## Manifest (junto al video)
```json
{
  "model": "wan",
  "task": "text_to_video",
  "prompt": "...",
  "seed": 12345,
  "steps": 50,
  "fps": 16,
  "frames": 81,
  "guidance_scale": 5.0,
  "resolution": {"width": 832, "height": 480},
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
- `InspectModelStep` comparte la instancia del provider con `LoadModelStep` (no se crean duplicados).
