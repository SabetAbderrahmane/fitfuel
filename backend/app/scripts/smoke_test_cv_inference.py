from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.photo_service import PhotoService
from app.services.vision_inference_service import get_vision_inference_service


def require_artifact(path_value: str, label: str) -> None:
    path = Path(path_value)
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test FitFuel CV inference artifacts.")
    parser.add_argument("--image", required=True, help="Local JPG/PNG/WebP image path")
    parser.add_argument("--top-k", type=int, default=settings.vision_top_k)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    require_artifact(settings.vision_binary_model_path, "binary model checkpoint")
    require_artifact(settings.vision_binary_class_names_path, "binary class names")
    require_artifact(settings.vision_food_model_path, "food model checkpoint")
    require_artifact(settings.vision_food_class_names_path, "food class names")

    with Image.open(image_path) as image:
        inference = get_vision_inference_service().analyze(
            image=image.convert("RGB"),
            top_k=max(1, min(args.top_k, 10)),
        )

    binary = inference.binary_prediction
    print("Binary result:")
    print(f"  predicted_label: {binary.predicted_label}")
    print(f"  food_probability: {binary.food_probability:.4f}")
    print(f"  confidence: {binary.confidence:.4f}")
    print(f"  status: {binary.status}")

    if inference.food_prediction is None:
        print("Food classifier was skipped.")
        return

    food_prediction = inference.food_prediction
    print("Food classifier result:")
    print(f"  predicted_label: {food_prediction.predicted_label}")
    print(f"  confidence: {food_prediction.confidence:.4f}")
    print(f"  status: {food_prediction.status}")
    print("  top_k:")
    for candidate in food_prediction.top_k:
        print(f"    {candidate.label}: {candidate.probability:.4f}")

    try:
        db = SessionLocal()
        try:
            photo_service = PhotoService(db)
            food_item, match_score, match_strategy, _label, requires_confirmation = (
                photo_service._match_food_item_by_label(food_prediction.predicted_label)
            )
            nutrition = photo_service._build_nutrition_estimate_response(
                food_item=food_item,
                serving_grams=settings.vision_default_serving_grams,
            )
        finally:
            db.close()
    except Exception as exc:
        print(f"Mapping/nutrition check skipped: {exc}")
        return

    if food_item is None:
        print("Mapping result: unmapped")
        return

    print("Mapping result:")
    print(f"  food_item_id: {food_item.id}")
    print(f"  food_name: {food_item.display_name or food_item.name}")
    print(f"  match_strategy: {match_strategy}")
    print(f"  match_score: {match_score}")
    print(f"  requires_confirmation: {requires_confirmation}")
    if nutrition is None:
        print("Nutrition estimate: unavailable")
        return

    print("Nutrition estimate:")
    print(f"  serving_grams: {nutrition.serving_grams}")
    print(f"  estimated_calories: {nutrition.estimated_calories}")
    print(f"  estimated_protein_g: {nutrition.estimated_protein_g}")
    print(f"  estimated_carbs_g: {nutrition.estimated_carbs_g}")
    print(f"  estimated_fat_g: {nutrition.estimated_fat_g}")


if __name__ == "__main__":
    main()
