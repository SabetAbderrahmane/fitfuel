from __future__ import annotations

import json
import threading
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from app.ai.vision.confidence import PredictionCandidate, get_top_k_predictions
from app.core.config import settings


@dataclass(slots=True)
class VisionInferenceResult:
    model_name: str
    predicted_label: str
    confidence_score: float
    top_predictions: list[PredictionCandidate]


class ResNet50VisionClassifier:
    """
    Lazy-loaded ResNet50 inference wrapper.

    Improvements in this version:
    - thread-safe model load
    - explicit warm-up support
    - startup preloading support
    - CUDA autocast path when GPU is available and selected
    - less user-facing cold-start latency
    """

    def __init__(self) -> None:
        self._model = None
        self._preprocess = None
        self._class_names: list[str] = []
        self._device = None
        self._model_name = "uninitialized"
        self._load_lock = threading.Lock()
        self._is_warmed = False
        self._use_cuda_autocast = False

    @staticmethod
    def _load_class_names(file_path: str) -> list[str]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Class names file not found: {file_path}")

        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("Class names JSON must be an array of strings.")
            return [str(item).strip() for item in data if str(item).strip()]

        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @staticmethod
    def _extract_state_dict(loaded_object):
        if isinstance(loaded_object, dict):
            if "state_dict" in loaded_object and isinstance(loaded_object["state_dict"], dict):
                return loaded_object["state_dict"]
            return loaded_object
        return loaded_object

    @staticmethod
    def _strip_module_prefix(state_dict: dict) -> dict:
        cleaned: dict = {}
        for key, value in state_dict.items():
            if key.startswith("module."):
                cleaned[key[len("module."):]] = value
            else:
                cleaned[key] = value
        return cleaned

    @staticmethod
    def _resolve_device(torch):
        requested_device = settings.vision_device.strip().lower()

        if requested_device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")

        if (
            requested_device == "mps"
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            return torch.device("mps")

        return torch.device("cpu")

    def _load_model(self) -> None:
        if self._model is not None:
            return

        with self._load_lock:
            if self._model is not None:
                return

            try:
                import torch
                import torch.nn as nn
                from torchvision.models import ResNet50_Weights, resnet50
            except ImportError as exc:
                raise RuntimeError(
                    "Torch/TorchVision are not installed. "
                    "Install torch, torchvision, and pillow before using the inference endpoint."
                ) from exc

            if hasattr(torch, "set_float32_matmul_precision"):
                torch.set_float32_matmul_precision("high")

            device = self._resolve_device(torch)

            if device.type == "cuda":
                torch.backends.cudnn.benchmark = True

            custom_model_path = settings.vision_model_path.strip()
            class_names_path = settings.vision_class_names_path.strip()

            weights = ResNet50_Weights.DEFAULT
            preprocess = weights.transforms()

            if custom_model_path and class_names_path and Path(custom_model_path).exists():
                class_names = self._load_class_names(class_names_path)
                if not class_names:
                    raise RuntimeError("Custom class names file is empty.")

                model = resnet50(weights=None)
                in_features = model.fc.in_features
                model.fc = nn.Linear(in_features, len(class_names))

                checkpoint = torch.load(custom_model_path, map_location=device)
                state_dict = self._extract_state_dict(checkpoint)
                state_dict = self._strip_module_prefix(state_dict)
                model.load_state_dict(state_dict, strict=True)
                model_name = f"resnet50_custom:{Path(custom_model_path).name}"
            else:
                model = resnet50(weights=weights)
                class_names = list(weights.meta.get("categories", []))
                model_name = f"resnet50_pretrained:{weights.__class__.__name__}.DEFAULT"

            model.eval()
            model.to(device)

            self._model = model
            self._preprocess = preprocess
            self._class_names = class_names
            self._device = device
            self._model_name = model_name
            self._use_cuda_autocast = device.type == "cuda"

    def warm_up(self) -> None:
        """
        Force model initialization and run one dummy forward pass so the first
        real user request does not absorb the cold-start cost.
        """
        self._load_model()

        if self._is_warmed:
            return

        with self._load_lock:
            if self._is_warmed:
                return

            assert self._model is not None
            assert self._preprocess is not None
            assert self._device is not None

            import torch

            dummy_image = Image.new("RGB", (224, 224), color=(127, 127, 127))
            batch = self._preprocess(dummy_image).unsqueeze(0)

            if self._device.type == "cuda":
                batch = batch.to(self._device, non_blocking=True)
                autocast_ctx = torch.autocast(device_type="cuda", dtype=torch.float16)
            else:
                batch = batch.to(self._device)
                autocast_ctx = nullcontext()

            with torch.inference_mode():
                with autocast_ctx:
                    _ = self._model(batch)

            if self._device.type == "cuda":
                torch.cuda.synchronize()

            self._is_warmed = True

    def infer_pil_image(
        self,
        image,
        top_k: int = 3,
    ) -> VisionInferenceResult:
        self._load_model()

        assert self._model is not None
        assert self._preprocess is not None
        assert self._device is not None

        import torch

        batch = self._preprocess(image).unsqueeze(0)

        if self._device.type == "cuda":
            batch = batch.to(self._device, non_blocking=True)
            autocast_ctx = torch.autocast(device_type="cuda", dtype=torch.float16)
        else:
            batch = batch.to(self._device)
            autocast_ctx = nullcontext()

        with torch.inference_mode():
            with autocast_ctx:
                logits = self._model(batch)

        candidates = get_top_k_predictions(
            logits=logits,
            class_names=self._class_names,
            top_k=max(1, min(top_k, 10)),
        )
        top_candidate = candidates[0]

        return VisionInferenceResult(
            model_name=self._model_name,
            predicted_label=top_candidate.label,
            confidence_score=top_candidate.confidence_score,
            top_predictions=candidates,
        )


_classifier_instance: ResNet50VisionClassifier | None = None
_classifier_lock = threading.Lock()


def get_vision_classifier() -> ResNet50VisionClassifier:
    global _classifier_instance

    if _classifier_instance is None:
        with _classifier_lock:
            if _classifier_instance is None:
                _classifier_instance = ResNet50VisionClassifier()

    return _classifier_instance