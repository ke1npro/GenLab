import os
import sys


def detect_environment() -> dict:
    is_colab = _is_colab()
    return {
        "type": "colab" if is_colab else "local",
        "is_colab": is_colab,
        "is_local": not is_colab,
        "is_interactive": bool(sys.stdin and sys.stdin.isatty()),
        "python": sys.version,
    }


def _is_colab() -> bool:
    if "COLAB_GPU" in os.environ:
        return True
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False
    except Exception:
        return False


def is_colab() -> bool:
    return detect_environment()["is_colab"]
