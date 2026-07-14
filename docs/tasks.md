# Tasks — GenLab

Una Task = una intención con esquema de entrada/salida. Valida contra `provider.capabilities`.

## Tasks implementadas

### text_to_video
- **Registry**: `@register_task("text_to_video")`
- **Clase**: `TextToVideoTask`
- **Entradas**:
  - `prompt` (str, requerido) — descripción del video
  - `negative_prompt` (str, opcional) — lo que NO debe aparecer
  - `seed` (int, opcional) — semilla para reproducibilidad
  - `steps` / `num_inference_steps` (int, default: 50)
  - `frames` / `num_frames` (int, default: 81)
  - `fps` (int, default: 16)
  - `resolution` (dict: width/height, default: 832x480)
  - `guidance_scale` (float, default: 5.0)
- **Salidas**: `frames` (lista de PIL Images), exportado como `.mp4`
- **Nota**: Los defaults corresponden al modelo `wan`. Cada modelo puede sobreescribirlos en su `configs/models/<nombre>.yaml`.

### text_to_image — NUEVO
- **Registry**: `@register_task("text_to_image")`
- **Clase**: `TextToImageTask`
- **Entradas**:
  - `prompt` (str, requerido) — descripción de la imagen
  - `negative_prompt` (str, opcional) — lo que NO debe aparecer
  - `seed` (int, opcional) — semilla para reproducibilidad
  - `steps` / `num_inference_steps` (int, default: 50)
  - `resolution` (dict: width/height, default: 1024x1024)
  - `guidance_scale` (float, default: 7.0)
- **Salidas**: `image` (PIL Image), exportado como `.png`
- **Modelos compatibles**: `flux` (FLUX.1-schnell, 4 pasos), `sdxl` (SDXL 1.0, 50 pasos)

## Selección automática de tarea

En el notebook, al elegir un modelo, la tarea se selecciona automáticamente:
- Modelos de video (`wan`, `cogvideo`) → `text_to_video`
- Modelos de imagen (`flux`, `sdxl`) → `text_to_image`

## Estado completo

| Task | Entradas | Salidas | Compatibilidad | Estado |
|---|---|---|---|---|
| text_to_video | prompt, seed, steps, frames, fps, resolution | video (.mp4) | `supports_text_to_video` | ✅ |
| text_to_image | prompt, seed, steps, resolution | image (.png) | `supports_text_to_image` | ✅ |
| image_to_video | image, prompt | video | `supports_image_to_video` | Beta |
| image_to_image | image, prompt, strength | image | `supports_image_to_image` | Beta |
| inpainting | image, mask, prompt | image | `supports_inpainting` | Beta (stub) |

## Reglas
- `BaseTask` con `validate(provider)`, `prepare_inputs()`, `postprocess()`.
- `validate()` usa `provider.capabilities`, nunca `isinstance`.
- No ejecuta inferencia; delega al pipeline step `generate`.
- Decorar con `@register_task("<nombre>")`.
- Documentar aquí entradas/salidas al crear.
