from __future__ import annotations

import os
from pathlib import Path

from genlab.config.loader import load_config
from genlab.core.environment import detect_environment
from genlab.core.hardware import check_disk_free, detect_hardware
from genlab.core.paths import resolve_paths


def bootstrap(config_dir: str | Path | None = None) -> dict:
    env = detect_environment()
    hw = detect_hardware()
    paths = resolve_paths(config_dir or "configs")

    _ensure_dirs(paths)

    config = _try_load_config(paths["config_dir"])

    hf_status = _check_hf_token()

    report = _build_report(env, hw, paths, hf_status)
    _print_report(report)

    return {
        "environment": env,
        "hardware": hw,
        "paths": paths,
        "hf_token_ok": hf_status,
        "config": config,
        "report": report,
    }


def _ensure_dirs(paths: dict) -> None:
    for key in ("output_dir", "temp_dir", "cache_dir", "runs_dir"):
        path = paths.get(key)
        if path:
            Path(path).mkdir(parents=True, exist_ok=True)


def _try_load_config(config_dir: str):
    try:
        return load_config(config_dir=config_dir)
    except Exception:
        return None


def _check_hf_token() -> bool:
    token = os.environ.get("HF_TOKEN")
    if token:
        return True
    try:
        from huggingface_hub import get_token
        return get_token() is not None
    except ImportError:
        return False
    except Exception:
        return False


def _build_report(env: dict, hw: dict, paths: dict, hf_ok: bool) -> list[tuple[str, str]]:
    return [
        ("Entorno", env["type"].upper()),
        ("GPU", hw["gpu"]),
        ("VRAM", f'{hw["vram_gb"]} GB' if hw["vram_gb"] else "N/A"),
        ("RAM", f'{hw["ram_gb"]} GB' if hw["ram_gb"] else "N/A"),
        ("CUDA", hw["cuda_version"]),
        ("Drive", "OK" if env["is_colab"] and paths.get("drive_base") else "N/A"),
        ("Internet", "OK"),
        ("HF Token", "OK" if hf_ok else "NO CONFIGURADO"),
        ("Espacio libre", f'{check_disk_free()} GB'),
        ("Cache modelos", paths.get("cache_dir", "N/A")),
    ]


def _print_report(report: list[tuple[str, str]]) -> None:
    sep = "-" * 50
    print(sep)
    print("  GenLab — Diagnóstico")
    print(sep)
    for label, value in report:
        print(f"  {label:<16} {value}")
    print(sep)

    gpu_entry = next((v for k, v in report if k == "GPU"), "")
    if gpu_entry in ("N/A", ""):
        warn = (
            "  ⚠  NO SE DETECTÓ GPU\n"
            "  Para generar video necesitas una GPU (T4+ en Colab).\n"
            "  → Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU"
        )
        print(warn)
        print(sep)
