from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class VisionModelUnavailableError(RuntimeError):
    """Raised when configured CV artifacts or ML dependencies are unavailable."""


@dataclass(slots=True)
class VisionPrediction:
    label: str
    probability: float


@dataclass(slots=True)
class BinaryVisionResult:
    predicted_label: str
    food_probability: float
    confidence: float
    status: Literal["accepted", "rejected", "uncertain"]
    user_confirmation_required: bool
    message: str | None


@dataclass(slots=True)
class FoodVisionResult:
    predicted_label: str
    confidence: float
    status: Literal["accepted", "uncertain"]
    user_confirmation_required: bool
    top_k: list[VisionPrediction]


@dataclass(slots=True)
class FullVisionResult:
    binary_prediction: BinaryVisionResult
    food_prediction: FoodVisionResult | None


@dataclass(slots=True)
class _LoadedModel:
    model: Any
    class_names: list[str]


class VisionInferenceService:
    """
    Lazy, cached inference service for the FitFuel ResNet50 CV models.
    """

    def __init__(self) -> None:
        self._binary_model: _LoadedModel | None = None
        self._food_model: _LoadedModel | None = None
        self._transform = None
        self._device = None
        self._lock = threading.Lock()
        self._logged_device = False

    @staticmethod
    def _load_class_names(path: str | Path) -> list[str]:
        class_path = Path(path)
        if not class_path.exists():
            raise VisionModelUnavailableError(f"Vision class names file not found: {class_path}")
        data = json.loads(class_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise VisionModelUnavailableError(f"Vision class names JSON must be an array: {class_path}")
        class_names = [str(item).strip() for item in data if str(item).strip()]
        if not class_names:
            raise VisionModelUnavailableError(f"Vision class names file is empty: {class_path}")
        return class_names

    @staticmethod
    def _extract_state_dict(checkpoint: Any) -> dict[str, Any]:
        if not isinstance(checkpoint, dict):
            raise VisionModelUnavailableError("Vision checkpoint must be a dictionary.")
        if "model_state_dict" in checkpoint and isinstance(checkpoint["model_state_dict"], dict):
            return checkpoint["model_state_dict"]
        if "state_dict" in checkpoint and isinstance(checkpoint["state_dict"], dict):
            return checkpoint["state_dict"]
        return checkpoint

    @staticmethod
    def _strip_module_prefix(state_dict: dict[str, Any]) -> dict[str, Any]:
        return {
            key.removeprefix("module."): value
            for key, value in state_dict.items()
        }

    @staticmethod
    def _resolve_device(torch: Any):
        requested = settings.vision_device.strip().lower()
        if requested == "auto":
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif requested == "cuda":
            if not torch.cuda.is_available():
                raise VisionModelUnavailableError(
                    "VISION_DEVICE=cuda was requested, but CUDA is not available."
                )
            device = torch.device("cuda")
        elif requested == "cpu":
            device = torch.device("cpu")
        else:
            raise VisionModelUnavailableError("VISION_DEVICE must be 'auto', 'cuda', or 'cpu'.")
        return device

    def _imports(self):
        try:
            import torch
            import torch.nn as nn
            from torchvision import models, transforms
        except ImportError as exc:
            raise VisionModelUnavailableError(
                "Torch/TorchVision are not installed. Install torch and torchvision to use CV inference."
            ) from exc
        return torch, nn, models, transforms

    def _get_transform(self):
        if self._transform is not None:
            return self._transform
        _torch, _nn, _models, transforms = self._imports()
        self._transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ]
        )
        return self._transform

    def _get_device(self):
        if self._device is not None:
            return self._device
        torch, _nn, _models, _transforms = self._imports()
        self._device = self._resolve_device(torch)
        if not self._logged_device:
            logger.info("Selected vision inference device: %s", self._device)
            print(f"Selected vision inference device: {self._device}")
            self._logged_device = True
        return self._device

    def _load_model(
        self,
        *,
        model_path: str,
        class_names_path: str,
        model_label: str,
    ) -> _LoadedModel:
        path = Path(model_path)
        if not path.exists():
            raise VisionModelUnavailableError(f"{model_label} model checkpoint not found: {path}")

        class_names = self._load_class_names(class_names_path)
        torch, nn, models, _transforms = self._imports()
        device = self._get_device()

        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, len(class_names))

        checkpoint = torch.load(path, map_location=device)
        state_dict = self._strip_module_prefix(self._extract_state_dict(checkpoint))
        model.load_state_dict(state_dict, strict=True)
        model.to(device)
        model.eval()
        return _LoadedModel(model=model, class_names=class_names)

    def _get_binary_model(self) -> _LoadedModel:
        if self._binary_model is None:
            with self._lock:
                if self._binary_model is None:
                    self._binary_model = self._load_model(
                        model_path=settings.vision_binary_model_path,
                        class_names_path=settings.vision_binary_class_names_path,
                        model_label="Binary",
                    )
        return self._binary_model

    def _get_food_model(self) -> _LoadedModel:
        if self._food_model is None:
            with self._lock:
                if self._food_model is None:
                    self._food_model = self._load_model(
                        model_path=settings.vision_food_model_path,
                        class_names_path=settings.vision_food_class_names_path,
                        model_label="Food classifier",
                    )
        return self._food_model

    def _predict(self, loaded: _LoadedModel, image: Image.Image, top_k: int) -> list[VisionPrediction]:
        torch, _nn, _models, _transforms = self._imports()
        transform = self._get_transform()
        device = self._get_device()
        batch = transform(image.convert("RGB")).unsqueeze(0).to(device)

        with torch.inference_mode():
            logits = loaded.model(batch)
            probabilities = torch.softmax(logits, dim=1).squeeze(0).detach().cpu()

        top_count = min(max(1, top_k), len(loaded.class_names))
        top_probs, top_indices = torch.topk(probabilities, k=top_count)
        return [
            VisionPrediction(
                label=loaded.class_names[int(index)],
                probability=round(float(probability), 6),
            )
            for probability, index in zip(top_probs.tolist(), top_indices.tolist(), strict=False)
        ]

    def run_binary_gate(self, image: Image.Image) -> BinaryVisionResult:
        loaded = self._get_binary_model()
        predictions = self._predict(loaded, image, top_k=len(loaded.class_names))
        top = predictions[0]

        food_probability = 0.0
        for prediction in predictions:
            if prediction.label == "food":
                food_probability = prediction.probability
                break

        accepted = top.label == "food" and food_probability >= settings.vision_food_accept_threshold
        rejected = top.label == "non_food" and top.probability >= settings.vision_food_accept_threshold
        status: Literal["accepted", "rejected", "uncertain"]
        if accepted:
            status = "accepted"
        elif rejected:
            status = "rejected"
        else:
            status = "uncertain"

        return BinaryVisionResult(
            predicted_label=top.label,
            food_probability=food_probability,
            confidence=top.probability,
            status=status,
            user_confirmation_required=status == "uncertain",
            message=None if status == "accepted" else "Image does not confidently appear to contain food.",
        )

    def run_food_classifier(self, image: Image.Image, top_k: int | None = None) -> FoodVisionResult:
        loaded = self._get_food_model()
        predictions = self._predict(loaded, image, top_k=top_k or settings.vision_top_k)
        top = predictions[0]
        accepted = top.probability >= settings.vision_class_accept_threshold
        return FoodVisionResult(
            predicted_label=top.label,
            confidence=top.probability,
            status="accepted" if accepted else "uncertain",
            user_confirmation_required=not accepted,
            top_k=predictions,
        )

    def analyze(self, image: Image.Image, top_k: int | None = None) -> FullVisionResult:
        binary = self.run_binary_gate(image)
        if binary.status != "accepted":
            return FullVisionResult(binary_prediction=binary, food_prediction=None)
        food = self.run_food_classifier(image, top_k=top_k)
        return FullVisionResult(binary_prediction=binary, food_prediction=food)


_vision_inference_service: VisionInferenceService | None = None
_vision_inference_lock = threading.Lock()


def get_vision_inference_service() -> VisionInferenceService:
    global _vision_inference_service
    if _vision_inference_service is None:
        with _vision_inference_lock:
            if _vision_inference_service is None:
                _vision_inference_service = VisionInferenceService()
    return _vision_inference_service
