# Providers — GenLab

Cada Provider = un modelo. Solo inferencia. Assets resueltos por `AssetManager` (descarga paralela solo archivos necesarios).

## Providers implementados

### wan (MVP 1.5)
- **Registry**: `@register_provider("wan")`
- **Clase**: `WanT2VProvider`
- **Modelo**: `Wan-AI/Wan2.1-T2V-1.3B-Diffusers`
- **Pipeline**: `WanPipeline` (diffusers >= 0.33.0)
- **Tareas**: `text_to_video`
- **VRAM**: ~11 GB (enable_model_cpu_offload)
- **Descarga**: ~9 GB (solo archivos necesarios via `allow_patterns`)
- **Licencia**: Apache 2.0
- **Hardware**: T4 compatible con offload

### cogvideo
- **Registry**: `@register_provider("cogvideo")`
- **Clase**: `CogVideoProvider`
- **Modelo**: `zai-org/CogVideoX-2b` (mirror ligero)
- **Pipeline**: `CogVideoXPipeline` (diffusers)
- **Tareas**: `text_to_video`, `image_to_video`
- **VRAM**: ~15 GB (enable_model_cpu_offload)
- **Descarga**: ~9 GB (via `allow_patterns`)
- **Licencia**: Apache 2.0
- **Hardware**: T4 con offload (límite)

### flux — NUEVO
- **Registry**: `@register_provider("flux")`
- **Clase**: `FluxProvider`
- **Modelo**: `black-forest-labs/FLUX.1-schnell` (por defecto)
- **Pipeline**: `FluxPipeline` (diffusers)
- **Tareas**: `text_to_image`
- **VRAM**: ~12 GB (enable_model_cpu_offload)
- **Descarga**: ~12 GB (incluye T5 text_encoder_2)
- **Licencia**: Apache 2.0 (schnell)
- **Hardware**: T4 compatible
- **Notas**: 4 pasos de inferencia por defecto, guidance_scale=0.0. Requiere `text_encoder_2/*` y `tokenizer_2/*` en patrones.

### sdxl — NUEVO
- **Registry**: `@register_provider("sdxl")`
- **Clase**: `SDXLProvider`
- **Modelo**: `stabilityai/stable-diffusion-xl-base-1.0`
- **Pipeline**: `StableDiffusionXLPipeline` (diffusers)
- **Tareas**: `text_to_image`
- **VRAM**: ~8 GB (enable_model_cpu_offload)
- **Descarga**: ~7 GB
- **Licencia**: OpenRAIL-M
- **Hardware**: T4 compatible

## AssetManager

Cada provider declara los archivos que necesita mediante `get_required_files()` (glob patterns).  
`AssetManager` usa `snapshot_download` con `allow_patterns` para descargar **solo** esos archivos con **8 hilos paralelos** (`max_workers=8`), más `hf_transfer` como acelerador Rust cuando está disponible.

```python
class WanT2VProvider(BaseProvider):
    def get_required_files(self) -> list[str]:
        return ["model_index.json", "scheduler/*", "text_encoder/*",
                "tokenizer/*", "transformer/*", "vae/*"]
```

Para repositorios con múltiples variantes (LTX, WAN 13B, etc.) esto evita descargar cientos de GB de modelos alternativos.

## ModelInspector

Antes de descargar, `ModelInspector` muestra:
- Menú de estrategia de descarga (1: selectivo, 2: completo)
- Modelo y tareas soportadas
- Licencia y VRAM estimada
- Tamaño del repositorio vs descarga estimada
- Espacio libre en disco
- Estado de `hf_transfer`
- Tiempo estimado (basado en sonda de ancho de banda)
- Confirmación interactiva (s/N)

## Estado completo

| Provider | Tareas | VRAM | Descarga | Licencia | Offload | T4 | Estado |
|---|---|---|---|---|---|---|---|
| wan | text_to_video | ~11 GB | ~9 GB | Apache 2.0 | Sí | Sí | ✅ |
| cogvideo | text_to_video, image_to_video | ~15 GB | ~9 GB | Apache 2.0 | Sí | Límite | ✅ |
| flux | text_to_image | ~12 GB | ~12 GB | Apache 2.0 | Sí | Sí | ✅ |
| sdxl | text_to_image | ~8 GB | ~7 GB | OpenRAIL-M | Sí | Sí | ✅ |

## Reglas
- Hereda `BaseProvider`; implementa `load/generate/unload`.
- Declara `capabilities` (`supports_text_to_video`, etc.).
- Implementa `get_required_files()` — lista de glob patterns de archivos necesarios.
- Implementa `get_metadata()` — VRAM, licencia, descripción, hardware.
- `get_model_id()` se obtiene desde config (`model.model_id`) con fallback a `_default_model_id`.
- Decorar `@register_provider("<nombre>")`.
- Crear `config/models/<nombre>.yaml` con defaults.
- Nunca descarga pesos; usa `AssetManager` que resuelve solo los archivos necesarios.
