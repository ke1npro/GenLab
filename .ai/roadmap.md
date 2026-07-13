# Roadmap — GenLab

Ordenado por dependencia → impacto → dificultad. Criterio de éxito MVP:
`launcher.ipynb → prompt → video .mp4 en Drive`.

## MVP — "Un video real en Colab"

| Hito | Contenido | Depende de |
|---|---|---|
| 1.1 | Estructura + `pyproject` + `config/loader` (precedencia default<modelo<perfil<args) | — |
| 1.2 | `core/paths`, `core/hardware`, `bootstrap` + **reporte diagnóstico** | 1.1 |
| 1.3 | `BaseProvider` + `ModelManager` mínimo + `Task` base + Task registry mínimo | 1.2 |
| 1.4 | **Diseño Pipeline**: contrato de steps + orchestrator esqueleto | 1.3 |
| 1.5 | Provider `cogvideo` real (usa Manager para pesos) | 1.3, 1.4 |
| 1.6 | Tarea `text_to_video` + steps load→generate→export + **Manifest JSON** | 1.4, 1.5 |
| 1.7 | Servicios mínimos: huggingface (login), exporter (mp4+manifest), storage/local | 1.2 |
| 1.8 | `launcher.ipynb` (install, mount, pull, bootstrap+reporte, run, mostrar) | 1.6, 1.7 |

**Salida MVP**: video generado por prompt, reproducible vía manifest, sin editar código.

## Beta — "Multi-modelo, multi-tarea, robusto"

| Hito | Contenido |
|---|---|
| 2.1 | Provider `flux` (text_to_image, image_to_image) |
| 2.2 | Tareas text_to_image, image_to_image, inpainting(stub) + validación cruzada capabilities |
| 2.3 | **Perfiles completos** (low_vram, high_quality, balanced) + `config/environments` |
| 2.4 | Servicios robustos: caching real, drive sync, metrics |
| 2.5 | **Herramienta de benchmarking** (agrega manifests) |
| 2.6 | Optimización recursos (dtype/offload automático por estimate_memory) |
| 2.7 | Errores jerárquicos + reintentos HF |
| 2.8 | Providers `ltx`, `mochi`, `wan` |

**Salida Beta**: FLUX + CogVideoX por config; misma semilla → mismo video; reanudación re-descarga solo si `/content` se perdió; API opcional.

## v1.0 — "Producción y extensibilidad"

| Hito | Contenido |
|---|---|
| 3.1 | Suite tests (fake provider sin pesos) |
| 3.2 | CLI (`generate`, `models`, `doctor`) |
| 3.3 | Multi-entorno (local/vps) + storage backends |
| 3.4 | Documentación completa |
| 3.5 | Release (versionado, CHANGELOG, CI) |
| 3.6 | **API REST** (movida aquí desde Beta) |

## Future (post-v1.0)

- Sistema de Plugins formal
- Cola / Batch generation
- Reanudación tras caída de Colab
- UI Web
- Comparación automática avanzada de modelos

## Movimientos respecto al roadmap inicial

- API REST: **diferida** de Beta → v1.0 (no se usa pronto; reusa orchestrator, sin deuda).
- Plugins: **diferidos** a post-v1.0 (registry por decorador ya cubre el 90%).
- Pipeline: **adelantado** a 1.4 (fija el contrato del Provider).
- Perfiles: mecanismo en 1.1, perfiles completos en 2.3.
- Benchmark: captura en MVP (vía manifest), herramienta en 2.5.
