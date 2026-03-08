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
