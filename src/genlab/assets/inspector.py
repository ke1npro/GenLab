from __future__ import annotations

from typing import Any


class ModelInspector:
    def __init__(self, asset_manager: Any):
        self._am = asset_manager

    def inspect(self, provider: Any) -> dict[str, Any]:
        meta = provider.get_metadata()
        estimate = self._am.estimate(provider)
        cached = self._am.cached_path(provider.get_model_id())
        return {
            "metadata": meta,
            "download": estimate,
            "cached": cached is not None,
            "cached_path": str(cached) if cached else None,
        }

    def print_report(self, provider: Any) -> None:
        info = self.inspect(provider)
        meta = info["metadata"]
        dl = info["download"]

        print("=" * 56)
        print(f"  Modelo: {meta.get('model_id', '?')}")
        print(f"  Tarea:  {' | '.join(k.replace('supports_', '').replace('_', ' ') for k, v in provider.capabilities.items() if v)}")
        print(f"  Licencia: {meta.get('license', '?')}")
        print(f"  Hardware recomendado: {meta.get('hardware_compatibility', {})}")
        print(f"  VRAM estimada: {meta.get('estimated_vram_gb', '?')} GB")
        print(f"  Descripción: {meta.get('description', '')}")
        print("-" * 56)

        if info["cached"]:
            print(f"  [OK] Ya descargado en: {info['cached_path']}")
        else:
            print(f"  Archivos a descargar ({dl['file_count']} archivos, ~{dl['total_gb']} GB):")
            for f in dl["files"][:10]:
                print(f"    {f['path']}  ({f['size_gb']} GB)")
            if len(dl["files"]) > 10:
                print(f"    ... y {len(dl['files']) - 10} archivos más")
        print("=" * 56)

    def confirm(self, provider: Any) -> bool:
        self.print_report(provider)
        info = self.inspect(provider)
        if info["cached"]:
            return True
        dl = info["download"]
        print(f"\nSe descargarán ~{dl['total_gb']} GB.")
        respuesta = input("  ¿Continuar? (s/N): ").strip().lower()
        return respuesta == "s"
