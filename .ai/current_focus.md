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
MVP completo — todos los hitos 1.1–1.8 implementados y revisados.

## Estado
✅ **Listo para desplegar en Google Colab**

## Checklist de verificación pre-Colab

- [x] Sin imports circulares (fix: import diferido en `config/loader.py`)
- [x] `pyproject.toml` con deps ligeras por defecto; `[gpu]` y `[video]` como extras
- [x] Notebook con manejo robusto de HF token (Secrets → input manual → skip)
- [x] Variable `REPO_URL` editable en notebook
- [x] CogVideoProvider: separa CPU offload de GPU to()
- [x] Precedencia: default → env (colab/local) → modelo → perfil → args
- [x] Paths correctos en Colab (`/content/drive/MyDrive/GenLab/outputs`)
- [x] Cache propia (`/content/models_cache`) no interfiere con HF_HOME
- [x] Bootstrap detecta Colab automáticamente
- [x] Test suite: 28 tests, 26 pasando (2 require Pillow local)
- [x] Todos los docs actualizados

## Cómo desplegar
1. Subir a GitHub (repo público).
2. En Colab: Archivo → Abrir notebook → URL: `https://colab.research.google.com/github/USER/genlab/blob/main/notebooks/launcher.ipynb`
3. Configurar `HF_TOKEN` en Secrets de Colab.
4. Runtime → T4 GPU.
5. Ejecutar todas las celdas.

## Próximo paso
Beta 2.1 — Provider FLUX + tasks image

## Estructura final del MVP
```
src/genlab/
├── __init__.py / genlab.py     → API pública GenLab.run() / .bootstrap()
├── config/                      → schema.py + loader.py (precedencia 5 niveles)
├── core/                        → exceptions, environment, hardware, paths, bootstrap
├── models/                      → BaseProvider, ModelManager, registry, impl/cogvideo.py
├── tasks/                       → BaseTask, registry, text_to_video.py
├── pipeline/                    → orchestrator.py + steps.py (7 steps)
├── services/                    → huggingface.py, exporter.py
├── storage/                     → local.py
└── utils/                       → (vacío, preparado)
configs/{default,models,profiles,environments}/
notebooks/launcher.ipynb
tests/ (28 tests)
```
