# Bootstrap — GenLab

`bootstrap()` prepara el entorno y entrega un reporte diagnóstico.

## Orden de ejecución (implementado en `core/bootstrap.py`)
1. Detectar entorno (`core/environment.py`): ¿Colab (import google.colab / COLAB_GPU env var)? ¿local?
2. Detectar hardware (`core/hardware.py`): GPU, VRAM, RAM, CUDA (vía torch)
3. Detectar red: estado HF token (env var HF_TOKEN → huggingface_hub.get_token)
4. Detectar Drive: montado en Colab (por ruta)
5. Resolver paths (`core/paths.py`): Colab → `/content/drive/MyDrive/GenLab/...`; local → `./outputs/...`
6. Crear carpetas necesarias (outputs/runs, outputs/tmp, models_cache)
7. Inicializar configuración (cargar default.yaml + environ/{colab,local}.yaml según entorno)
8. Imprimir reporte diagnóstico

## Reporte diagnóstico (formato)
```
--------------------------------------------------
  GenLab — Diagnóstico
--------------------------------------------------
  Entorno          COLAB
  GPU              Tesla T4
  VRAM             15.8 GB
  RAM              12 GB
  CUDA             12.x
  Drive            OK
  Internet         OK
  HF Token         OK
  Espacio libre    XX GB
  Cache modelos    /content/models_cache
--------------------------------------------------
```

## Responsabilidades
- Preparar, no ejecutar generación.
- Fallar temprano solo si falta algo irrecuperable.
- No descargar modelos (eso es del `AssetManager` / `ModelManager`).

## Dependencias
- `core/environment.py`, `core/hardware.py`, `core/paths.py`, `config/loader.py`
- Opcional: `huggingface_hub` (para chequear token)
