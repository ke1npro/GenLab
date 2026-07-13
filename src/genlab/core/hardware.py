from __future__ import annotations

import os


def detect_hardware() -> dict:
    gpu_info = _detect_gpu()
    ram_gb = _detect_ram()
    return {
        "gpu": gpu_info.get("name", "N/A"),
        "vram_gb": gpu_info.get("vram_gb", 0),
        "ram_gb": ram_gb,
        "cuda_version": gpu_info.get("cuda_version", "N/A"),
        "has_cuda": gpu_info.get("has_cuda", False),
        "has_gpu": gpu_info.get("has_gpu", False),
    }


def _detect_gpu() -> dict:
    try:
        import torch
    except ImportError:
        return {"has_gpu": False, "has_cuda": False}

    if not torch.cuda.is_available():
        return {"has_gpu": False, "has_cuda": False}

    device_count = torch.cuda.device_count()
    if device_count == 0:
        return {"has_gpu": False, "has_cuda": True}

    props = torch.cuda.get_device_properties(0)
    vram_gb = round(props.total_memory / (1024**3), 1)
    cuda_version = torch.version.cuda or "N/A"

    return {
        "has_gpu": True,
        "has_cuda": True,
        "name": props.name,
        "vram_gb": vram_gb,
        "cuda_version": cuda_version,
        "device_count": device_count,
    }


def _detect_ram() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        return 0.0


def check_disk_free(path: str = ".") -> float:
    try:
        import shutil
        _, _, free = shutil.disk_usage(path)
        return round(free / (1024**3), 1)
    except Exception:
        return 0.0
