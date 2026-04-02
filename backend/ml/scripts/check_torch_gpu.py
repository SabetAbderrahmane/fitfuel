from __future__ import annotations

import platform

try:
    import torch
except ImportError as exc:
    raise SystemExit(
        "PyTorch is not installed in this environment. Install torch and torchvision with CUDA support first."
    ) from exc


def main() -> None:
    print("=== FitFuel Torch GPU Check ===")
    print(f"Python platform: {platform.platform()}")
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA runtime version (torch): {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")

        current_index = torch.cuda.current_device()
        print(f"Current GPU index: {current_index}")
        print(f"Current GPU name: {torch.cuda.get_device_name(current_index)}")

        x = torch.rand(3, 3, device="cuda")
        y = torch.rand(3, 3, device="cuda")
        z = x @ y

        print("GPU tensor test: OK")
        print("Sample tensor result:")
        print(z)
    else:
        print("CUDA is not available.")
        print("Check your PyTorch install, NVIDIA driver, and CUDA-compatible wheel.")


if __name__ == "__main__":
    main()