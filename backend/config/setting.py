import torch

def get_device():
    if torch.cuda.is_available():
        print(f"GPU Detected: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        print("GPU not found. Falling back to CPU.")
        return "cpu"
    
DEVICE = get_device()