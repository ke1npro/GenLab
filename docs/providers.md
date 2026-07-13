# Providers — GenLab

Cada Provider = un modelo. Solo inferencia. Pesos resueltos por `ModelManager`.

## Providers implementados

### cogvideo (MVP 1.5)
- **Registry**: `@register_provider("cogvideo")`
- **Clase**: `CogVideoProvider`
- **Modelo**: `THUDM/CogVideoX-2b`
- **Pipeline**: `CogVideoXPipeline` (diffusers)
- **Tareas**: `text_to_video`, `image_to_video`
- **Memoria est.**: ~TBD (T4 ~15GB)
- **Offload**: Sí (`enable_model_cpu_offload`)
- **Hardware**: CUDA (fallback a CPU sin GPU)

## Estado completo

| Provider | Tareas soportadas | Memoria est. | Requisitos | Limitaciones | Estado |
|---|---|---|---|---|---|
| cogvideo | text_to_video, image_to_video | ~13-15GB | diffusers, CUDA | calidad/media, lenta en T4 | MVP (1.5) |
| ltx | text_to_video | ~5-6GB | diffusers, CUDA | resolución fija 768x512 | MVP (1.5) |
| flux | text_to_image, image_to_image | ~TBD | diffusers | no video | Beta (2.1) |
| ltx | text_to_video | ~TBD | diffusers | — | Beta (2.8) |
| mochi | text_to_video | alta | diffusers | VRAM alta | Beta (2.8) |
| wan | text_to_video, image_to_video | ~TBD | diffusers | — | Beta (2.8) |
| hunyuan | text_to_video | muy alta | diffusers | VRAM muy alta | Future |

## Reglas
- Hereda `BaseProvider`; implementa `load/generate/unload/estimate_memory`.
- Declara `capabilities` (`supports_text_to_video`, etc.).
- Decorar `@register_provider("<nombre>")`.
- Crear `config/models/<nombre>.yaml`.
- Nunca descarga pesos; pídelos al `ModelManager`.
- El método `get_model_id()` devuelve el repo ID de Hugging Face.
