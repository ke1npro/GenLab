# Current Focus — GenLab

> Punto de entrada para agentes de IA (Opencode/DeepSeek y futuros).
> ÚNICO documento efímero del proyecto; el resto de la doc es estable.
> REGLA OBLIGATORIA: antes de implementar cualquier tarea importante, lee en orden:
>   1. .ai/current_focus.md
>   2. .ai/project_context.md
>   3. .ai/architecture.md
>   4. .ai/coding_rules.md
> Si el hito cambia, este archivo se actualiza automáticamente.

## Hito actual
Generación de imágenes + descargas optimizadas.

## Estado
✅ **Enfoque en generación de imágenes (Flux/SDXL) con descargas optimizadas**

## Logros alcanzados

- [x] AssetManager optimizado: `max_workers=8`, `hf_transfer` automático, verificación de espacio, sonda de ancho de banda, diagnóstico completo
- [x] ModelInspector con menú de estrategia de descarga (selectivo/completo) y reporte diagnóstico detallado
- [x] Cache HF con symlinks para reutilizar blobs cacheados
- [x] Providers: Flux (FLUX.1-schnell) y SDXL (Stable Diffusion XL 1.0) para `text_to_image`
- [x] Task: `text_to_image` con exportación a PNG
- [x] Pipeline adaptado: ExportStep maneja imágenes (`.png`) y videos (`.mp4`) según salida
- [x] Notebook con menú interactivo numerado para elegir modelo + model_id personalizado
- [x] Provider configurable: `get_model_id()` lee desde config YAML con fallback a hardcoded
- [x] `GenLabConfig` convertido a dict en todos los steps (`_cfg_to_dict`)
- [x] Tests: 49 tests, 1 skip (huggingface-hub no instalado localmente)
- [x] Docs actualizados: providers, tasks, pipeline, bootstrap

## Cómo desplegar
1. Subir a GitHub (repo público).
2. En Colab: Archivo → Abrir notebook → URL: `https://colab.research.google.com/github/USER/genlab/blob/main/notebooks/launcher.ipynb`
3. Configurar `HF_TOKEN` en Secrets de Colab.
4. Runtime → T4 GPU.
5. Ejecutar todas las celdas.

## Próximo paso
Beta 2.2 — image_to_image, inpainting, upscaling

## Estructura actual
```
src/genlab/
├── __init__.py / genlab.py     → API pública GenLab.run() / .bootstrap()
├── assets/                      → AssetManager + ModelInspector (descargas optimizadas)
├── config/                      → schema.py + loader.py (precedencia 5 niveles)
├── core/                        → exceptions, environment, hardware, paths, bootstrap
├── models/                      → BaseProvider, ModelManager, registry
│   └── impl/                    → wan, cogvideo, flux, sdxl
├── tasks/                       → BaseTask, registry, text_to_video, text_to_image
├── pipeline/                    → orchestrator.py + steps.py (8 steps)
├── services/                    → huggingface.py, exporter.py
├── storage/                     → local.py
└── utils/                       → (vacío, preparado)
configs/{default,environments,models,profiles}/
notebooks/launcher.ipynb
tests/ (49 tests)
```
