# Pipeline — GenLab

Flujo completo desde `launcher.ipynb` hasta el video/imagen exportada.

## Entrada
```python
GenLab().run(
    task="text_to_image",   # o "text_to_video"
    model="flux",           # o "wan", "cogvideo", "sdxl"
    prompt="...",
    config={'model': {'steps': 4, 'guidance_scale': 0.0}},
)
```

El parámetro `config` acepta cualquier clave de la jerarquía YAML (model, hardware, download, etc.).  
El namespace `model` se aplana automáticamente en `PrepareInputsStep` para pasarlo a `task.prepare_inputs()`.

La tarea se detecta automáticamente según el modelo en el notebook (video → `text_to_video`, imagen → `text_to_image`).

## Steps (implementados en `pipeline/steps.py`)

```
1. resolve_paths  → storage resuelve rutas (local/drive) según entorno
2. inspect_model  → ModelInspector: menú de estrategia + diagnóstico + confirmación
3. load_model     → AssetManager.resolve(provider) descarga paralela + Provider.load()
4. prepare_inputs → Task valida provider; prepara inputs según task
5. generate       → Provider.generate(inputs) -> outputs
6. postprocess    → Task.postprocess(outputs) -> resultado listo
7. export         → exporta .mp4 (video) o .png (imagen) + manifest.json
8. cleanup        → provider.unload(); liberar VRAM
```

**AssetManager** usa `snapshot_download` con:
- `allow_patterns` — descarga solo archivos necesarios del provider
- `max_workers=4` — descarga paralela con 4 hilos
- `hf_transfer` — acelerador Rust si está instalado (automático para descargas >500 MB)

**ExportStep** detecta el tipo de salida automáticamente:
- Si `result["image"]` existe → `export_image()` → `.png`
- Si `result["frames"]` existe → `export_video()` → `.mp4`

## Estrategia de descarga

Antes de descargar, el inspector ofrece un menú:
```
Opciones de descarga:
  1. Inteligente (solo archivos necesarios, hf_transfer si disponible)
  2. Completa (repo completo, sin filtros)
```

En modo **Inteligente** (default) solo se descargan los archivos que coinciden con `provider.get_required_files()`.  
Modo **Completa** descarga el repositorio entero.

## Contexto del pipeline
Cada step recibe y modifica un diccionario `ctx` compartido:
- `ctx["task"]`, `ctx["model"]` — parámetros de entrada
- `ctx["config"]` — configuración mergeada (GenLabConfig → convertida a dict)
- `ctx["paths"]` — rutas resueltas por entorno
- `ctx["_provider"]` — instancia del provider (creada en inspect, cargada en load)
- `ctx["_strategy"]` — estrategia de descarga ("selective" / "full")
- `ctx["provider"]` — provider listo para generar
- `ctx["inputs"]` — inputs preparados
- `ctx["outputs"]` — salida raw del provider
- `ctx["result"]` — salida postprocesada
- `ctx["video_path"]` / `ctx["image_path"]` — resultado final
- `ctx["manifest"]` — metadatos de la ejecución

## Manifest (junto al resultado)
```json
{
  "model": "flux",
  "task": "text_to_image",
  "prompt": "...",
  "seed": 12345,
  "steps": 4,
  "guidance_scale": 0.0,
  "resolution": {"width": 1024, "height": 1024},
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
- La estrategia de descarga elegida en `InspectModelStep` se propaga a `LoadModelStep` vía `ctx["_strategy"]`.
