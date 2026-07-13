# Tasks — GenLab

Una Task = una intención con esquema de entrada/salida. Valida contra `provider.capabilities`.

## Tasks implementadas

### text_to_video (MVP 1.6)
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
- **Salidas**: `frames` (lista de PIL Images/PIL.Image)
- **Nota**: Los defaults corresponden al modelo `wan` (Wan2.1 T2V 1.3B).  
  Cada modelo puede sobreescribirlos en su `configs/models/<nombre>.yaml`.

## Estado completo

| Task | Entradas | Salidas | Compatibilidad | Restricciones | Estado |
|---|---|---|---|---|---|
| text_to_video | prompt, (negative_prompt), seed, steps, frames, fps, resolution | video (mp4) | providers con `supports_text_to_video` | frames múltiplo de 8 (según modelo) | MVP (1.6) |
| image_to_video | image, prompt | video | `supports_image_to_video` | — | Beta |
| text_to_image | prompt | image | `supports_text_to_image` | — | Beta (2.2) |
| image_to_image | image, prompt, strength | image | `supports_image_to_image` | — | Beta (2.2) |
| inpainting | image, mask, prompt | image | `supports_inpainting` | requiere mask | Beta (2.2, stub) |
| upscaling | image, scale | image | `supports_upscaling` | — | Future |
| audio_generation | prompt, (duration) | audio | `supports_audio` | — | Future |

## Reglas
- `BaseTask` con `validate(provider)`, `prepare_inputs()`, `postprocess()`.
- `validate()` usa `provider.capabilities`, nunca `isinstance`.
- No ejecuta inferencia; delega al pipeline step `generate`.
- Decorar con `@register_task("<nombre>")`.
- Documentar aquí entradas/salidas al crear.
