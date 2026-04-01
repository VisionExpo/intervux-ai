import json
import os
from dataclasses import dataclass
from functools import lru_cache


def get_device() -> str:
    """
    Detects whether CUDA is available.
    Falls back safely if PyTorch or GPU is unavailable.
    """
    try:
        import torch

        if torch.cuda.is_available():
            # Test if CUDA actually works (handles driver/runtime mismatch)
            try:
                test_tensor = torch.zeros(1).cuda()
                device_name = torch.cuda.get_device_name(0)
                print(f"[INFO] GPU detected: {device_name}")
                return "cuda"
            except Exception as cuda_err:
                print(f"[WARN] CUDA available but not functional: {cuda_err}")
                print("[INFO] Falling back to CPU")

    except ImportError:
        print("[INFO] PyTorch not installed. Using CPU.")

    except Exception as e:
        print(f"[WARN] GPU detection failed: {e}")

    print("[INFO] Using CPU")
    return "cpu"


# Explicitly evaluated device (import-safe)
DEVICE = get_device()


@dataclass(frozen=True)
class AppSettings:
    cors_allow_origins: list[str]
    runtime_threadpool_workers: int


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    cors_raw = os.getenv("CORS_ALLOW_ORIGINS", '["http://localhost:5173"]')
    try:
        cors_allow_origins = json.loads(cors_raw)
        if not isinstance(cors_allow_origins, list):
            raise ValueError("CORS_ALLOW_ORIGINS must be a JSON array")
    except Exception:
        cors_allow_origins = ["http://localhost:5173"]

    workers = int(os.getenv("RUNTIME_THREADPOOL_WORKERS", "4"))
    workers = max(1, workers)

    return AppSettings(
        cors_allow_origins=cors_allow_origins,
        runtime_threadpool_workers=workers,
    )
