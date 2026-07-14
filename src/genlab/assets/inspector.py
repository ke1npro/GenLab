from __future__ import annotations

from typing import Any


_STRATEGY_FULL = "full"
_STRATEGY_SELECTIVE = "selective"


class ModelInspector:
    def __init__(self, asset_manager: Any):
        self._am = asset_manager
        self._strategy = _STRATEGY_SELECTIVE

    @property
    def strategy(self) -> str:
        return self._strategy

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

    def _menu(self, provider: Any) -> str:
        cached = self._am.cached_path(provider.get_model_id())
        if cached:
            return _STRATEGY_SELECTIVE

        print("\nOpciones de descarga:")
        print("  1. Inteligente (solo archivos necesarios, hf_transfer si disponible)")
        print("  2. Completa (repo completo, sin filtros)")
        opcion = input("\n  Elige (1/2) [1]: ").strip()
        self._strategy = _STRATEGY_FULL if opcion == "2" else _STRATEGY_SELECTIVE
        return self._strategy

    def _resolve_with_strategy(self, provider: Any) -> str:
        model_id = provider.get_model_id()
        if self._strategy == _STRATEGY_FULL:
            return self._am.resolve_raw(model_id)
        return self._am.resolve(provider)

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

    def diagnostic_report(self, provider: Any) -> dict[str, Any]:
        diag = self._am.diagnostic(provider)
        sep = "=" * 56
        print(sep)
        print("  Diagnóstico de descarga")
        print(sep)

        hf_status = "Activado" if diag["hf_transfer_active"] else "Disponible" if diag["hf_transfer_available"] else "No instalado"
        cache_status = "Descargado" if diag["cached"] else "No descargado"

        time_str = f"{diag['estimated_time_min']:.0f} minutos (~{diag['bandwidth_mbps']:.1f} MB/s)" if diag["bandwidth_mbps"] > 0 else "Desconocido"

        print(f"  {'Modelo:':<20} {diag['model_name']}")
        print(f"  {'Repositorio:':<20} {diag['repo_total_gb']} GB")
        print(f"  {'Descarga estim.:':<20} {diag['download_size_gb']} GB")
        print(f"  {'Espacio libre:':<20} {diag['free_space_gb']} GB")
        print(f"  {'hf_transfer:':<20} {hf_status}")
        print(f"  {'Tiempo estim.:':<20} {time_str}")
        print(f"  {'Caché HF:':<20} {cache_status}")
        if diag["cached"]:
            print(f"  {'Ruta:':<20} {diag['cached_path']}")
        print(f"  {'Modo:':<20} {'Selectivo' if self._strategy == _STRATEGY_SELECTIVE else 'Completo'}")
        print(sep)
        return diag

    def confirm(self, provider: Any) -> bool:
        info = self.inspect(provider)
        if info["cached"]:
            return True

        self._menu(provider)
        diag = self.diagnostic_report(provider)
        print(f"\nSe descargarán ~{diag['download_size_gb']} GB.")
        respuesta = input("  ¿Continuar? (s/N): ").strip().lower()
        return respuesta == "s"
