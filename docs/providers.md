# Providers — GenLab

Cada Provider = un modelo. Solo inferencia. Assets resueltos por `AssetManager` (descarga solo archivos necesarios).

## Providers implementados

### wan (MVP 1.5) — Default
- **Registry**: `@register_provider("wan")`
- **Clase**: `WanT2VProvider`
- **Modelo**: `Wan-AI/Wan2.1-T2V-1.3B-Diffusers`
- **Pipeline**: `WanPipeline` (diffusers >= 0.33.0)
- **Tareas**: `text_to_video`
- **VRAM**: ~11 GB (enable_model_cpu_offload)
- **Descarga**: ~12 GB (solo archivos necesarios via `allow_patterns`)
- **Licencia**: Apache 2.0
- **Hardware**: T4 compatible con offload

### cogvideo (MVP 1.5)
- **Registry**: `@register_provider("cogvideo")`
- **Clase**: `CogVideoProvider`
- **Modelo**: `THUDM/CogVideoX-2b`
- **Pipeline**: `CogVideoXPipeline` (diffusers)
- **Tareas**: `text_to_video`, `image_to_video`
- **VRAM**: ~15 GB (enable_model_cpu_offload)
- **Descarga**: ~13-15 GB (via `allow_patterns`)
- **Licencia**: Apache 2.0
- **Hardware**: T4 con offload (límite)

## AssetManager

Cada provider declara los archivos que necesita mediante `get_required_files()` (glob patterns).  
`AssetManager` usa `snapshot_download` con `allow_patterns` para descargar **solo** esos archivos, no el repositorio completo.

```python
class WanT2VProvider(BaseProvider):
    def get_required_files(self) -> list[str]:
        return [
            "model_index.json",
            "scheduler/*",
            "text_encoder/*",
            "tokenizer/*",
            "transformer/*",
            "vae/*",
        ]
```

Para repositorios con múltiples variantes (LTX, WAN 13B, etc.) esto evita descargar cientos de GB de modelos alternativos.

## ModelInspector

Antes de descargar, `ModelInspector` muestra:
- Modelo y tareas soportadas
- Licencia
- VRAM estimada
- Archivos individuales con peso
- Total estimado de descarga
- Confirmación interactiva (s/N)

## Estado completo

| Provider | Tareas | VRAM | Descarga | Licencia | Offload | T4 | Estado |
|---|---|---|---|---|---|---|---|
| wan | text_to_video | ~11 GB | ~12 GB | Apache 2.0 | Sí | Sí | MVP (1.5) |
| cogvideo | text_to_video, image_to_video | ~15 GB | ~13-15 GB | Apache 2.0 | Sí | Límite | MVP (1.5) |
| flux | text_to_image, image_to_image | TBD | TBD | — | — | — | Beta (2.1) |
| ltx | image_to_video | ~6 GB | ~2 GB | — | Sí | Sí | Beta (2.8) |
| mochi | text_to_video | alta | TBD | — | — | — | Beta (2.8) |
| hunyuan | text_to_video | muy alta | TBD | — | — | — | Future |

## Reglas
- Hereda `BaseProvider`; implementa `load/generate/unload`.
- Declara `capabilities` (`supports_text_to_video`, etc.).
- Implementa `get_required_files()` — lista de glob patterns de archivos necesarios.
- Implementa `get_metadata()` — VRAM, licencia, descripción, hardware.
- Implementa `get_model_id()` — repo ID de Hugging Face.
- Decorar `@register_provider("<nombre>")`.
- Crear `config/models/<nombre>.yaml` con defaults.
- Nunca descarga pesos; usa `AssetManager` que resuelve solo los archivos necesarios.
