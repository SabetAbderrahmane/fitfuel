from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap
from app.models.food_item import FoodItem
from app.models.nutrition_fact import NutritionFact
from app.models.photo_prediction import PhotoPrediction
from app.models.photo_prediction_candidate import PhotoPredictionCandidate
from app.models.photo_upload import PhotoUpload
from app.models.user import User
from app.schemas.photo import PhotoPredictionToFoodLogRequest
from app.scripts import seed_cv_label_food_maps as seed_module
from app.services.photo_service import PhotoService
from app.services.vision_inference_service import (
    BinaryVisionResult,
    FoodVisionResult,
    FullVisionResult,
    VisionInferenceService,
    VisionModelUnavailableError,
    VisionPrediction,
)


class FakeVisionService:
    def __init__(self, result: FullVisionResult) -> None:
        self.result = result

    def analyze(self, **_kwargs) -> FullVisionResult:
        return self.result


def create_test_image(tmp_path: Path) -> Path:
    image_path = tmp_path / "meal.jpg"
    Image.new("RGB", (32, 32), color=(240, 120, 80)).save(image_path)
    return image_path


def create_photo_upload(
    db_session: Session,
    test_user: User,
    image_path: Path,
) -> PhotoUpload:
    upload = PhotoUpload(
        user_id=test_user.id,
        original_filename=image_path.name,
        content_type="image/jpeg",
        file_size_bytes=image_path.stat().st_size,
        storage_provider="local",
        storage_key=image_path.name,
        local_file_path=str(image_path),
        upload_status="uploaded",
    )
    db_session.add(upload)
    db_session.commit()
    db_session.refresh(upload)
    return upload


def make_binary_result(label: str, food_probability: float, status: str) -> BinaryVisionResult:
    return BinaryVisionResult(
        predicted_label=label,
        food_probability=food_probability,
        confidence=max(food_probability, 1.0 - food_probability),
        status=status,
        user_confirmation_required=status == "uncertain",
        message=None if status == "accepted" else "Image does not confidently appear to contain food.",
    )


def make_food_result(
    label: str,
    confidence: float,
    status: str,
    alternatives: list[tuple[str, float]] | None = None,
) -> FoodVisionResult:
    top_k = [VisionPrediction(label=label, probability=confidence)]
    if alternatives is None:
        alternatives = [("sushi", round(1.0 - confidence, 4))]
    top_k.extend(VisionPrediction(label=alt_label, probability=probability) for alt_label, probability in alternatives)
    return FoodVisionResult(
        predicted_label=label,
        confidence=confidence,
        status=status,
        user_confirmation_required=status != "accepted",
        top_k=top_k,
    )


def test_missing_binary_artifact_raises_clear_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(settings, "vision_binary_model_path", str(tmp_path / "missing.pth"))
    monkeypatch.setattr(settings, "vision_binary_class_names_path", str(tmp_path / "missing.json"))

    service = VisionInferenceService()
    image = Image.new("RGB", (32, 32))

    with pytest.raises(VisionModelUnavailableError, match="Binary model checkpoint not found"):
        service.run_binary_gate(image)


def test_non_food_result_skips_food_classifier_and_persists_rejection(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("non_food", 0.02, "rejected"),
        food_prediction=None,
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=True)

    assert response.food_prediction is None
    assert response.binary_prediction is not None
    assert response.binary_prediction.status == "rejected"
    assert response.mapping_status == "unmapped"
    prediction = db_session.get(PhotoPrediction, response.saved_prediction_id)
    assert prediction is not None
    assert prediction.prediction_status == "rejected"


def test_low_confidence_food_classifier_returns_uncertain(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.97, "accepted"),
        food_prediction=make_food_result("steak", 0.59, "uncertain"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=False)

    assert response.food_prediction is not None
    assert response.food_prediction.status == "uncertain"
    assert response.food_prediction.user_confirmation_required is True
    assert response.mapping_status == "unmapped"


def test_pizza_returns_mapped_demo_nutrition_estimate(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    seed_module.seed_cv_label_food_maps(db_session)

    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.98, "accepted"),
        food_prediction=make_food_result("pizza", 0.96, "accepted"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(
        test_user,
        upload.id,
        save_prediction=True,
        serving_grams=150,
    )

    assert response.mapping_status == "mapped"
    assert response.nutrition_estimate is not None
    assert response.nutrition_estimate.food_name == "Pizza"
    assert response.nutrition_estimate.serving_grams == 150
    assert response.nutrition_estimate.estimated_calories == 399
    assert response.nutrition_estimate.estimated_protein_g == 16.5
    assert response.nutrition_estimate.estimated_carbs_g == 49.5
    assert response.nutrition_estimate.estimated_fat_g == 15


def test_unmapped_food_prediction_does_not_crash(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.98, "accepted"),
        food_prediction=make_food_result("ramen", 0.92, "accepted"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=True)

    assert response.mapping_status == "unmapped"
    assert response.nutrition_estimate is None
    assert response.food_prediction is not None
    assert response.food_prediction.top_k[0].label == "ramen"


def test_seed_script_creates_10_demo_mappings(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(seed_module, "REPORT_PATH", tmp_path / "cv-label-food-map-report.md")

    rows = seed_module.seed_cv_label_food_maps(db_session)

    assert len(rows) == 10
    assert {row["status"] for row in rows} == {"mapped"}
    label_count = db_session.scalar(select(func.count()).select_from(ClassifierLabel))
    mapping_count = db_session.scalar(select(func.count()).select_from(ClassifierLabelFoodMap))
    food_count = db_session.scalar(
        select(func.count()).select_from(FoodItem).where(FoodItem.source == seed_module.DEMO_SOURCE)
    )
    nutrition_count = db_session.scalar(select(func.count()).select_from(NutritionFact))
    assert label_count == 10
    assert mapping_count == 10
    assert food_count == 10
    assert nutrition_count == 10


def test_seed_cv_label_food_maps_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(seed_module, "REPORT_PATH", tmp_path / "cv-label-food-map-report.md")

    first_rows = seed_module.seed_cv_label_food_maps(db_session)
    second_rows = seed_module.seed_cv_label_food_maps(db_session)

    assert first_rows == second_rows
    assert db_session.scalar(select(func.count()).select_from(ClassifierLabel)) == 10
    assert db_session.scalar(select(func.count()).select_from(ClassifierLabelFoodMap)) == 10
    assert db_session.scalar(
        select(func.count()).select_from(FoodItem).where(FoodItem.source == seed_module.DEMO_SOURCE)
    ) == 10
    assert db_session.scalar(select(func.count()).select_from(NutritionFact)) == 10


def test_apple_pie_returns_mapped_demo_nutrition_estimate(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    seed_module.seed_cv_label_food_maps(db_session)
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.99, "accepted"),
        food_prediction=make_food_result("apple_pie", 0.93, "accepted"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=False)

    assert response.mapping_status == "mapped"
    assert response.matched_food_name == "Apple Pie"
    assert response.nutrition_estimate is not None
    assert response.nutrition_estimate.serving_grams == settings.vision_default_serving_grams
    assert response.nutrition_estimate.estimated_calories == 237
    assert response.nutrition_estimate.estimated_protein_g == 2.4
    assert response.nutrition_estimate.estimated_carbs_g == 34.0
    assert response.nutrition_estimate.estimated_fat_g == 11.0


def test_sushi_maps_to_demo_sushi_not_existing_brown_rice(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    brown_rice = FoodItem(
        name="brown rice",
        slug="brown-rice",
        normalized_name="brown rice",
        display_name="Brown Rice",
        search_name="brown rice",
        source="manual",
        is_active=True,
    )
    label = ClassifierLabel(
        label_set_name="food101_subset_resnet50",
        raw_label="sushi",
        normalized_label="sushi",
        display_label="Sushi",
    )
    db_session.add_all([brown_rice, label])
    db_session.flush()
    db_session.add(
        ClassifierLabelFoodMap(
            classifier_label_id=label.id,
            food_item_id=brown_rice.id,
            match_confidence=1.0,
            requires_user_confirmation=False,
        )
    )
    db_session.commit()
    seed_module.seed_cv_label_food_maps(db_session)

    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.99, "accepted"),
        food_prediction=make_food_result("sushi", 0.91, "accepted"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=False)

    assert response.mapping_status == "mapped"
    assert response.matched_food_name == "Sushi"
    assert response.matched_food_item_id != brown_rice.id
    assert response.nutrition_estimate is not None
    assert response.nutrition_estimate.estimated_calories == 145


def test_top_k_alternatives_are_candidates_not_detected_foods(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    seed_module.seed_cv_label_food_maps(db_session)
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.99, "accepted"),
        food_prediction=make_food_result(
            "apple_pie",
            0.94,
            "accepted",
            alternatives=[("sushi", 0.04), ("ramen", 0.02)],
        ),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )

    response = PhotoService(db_session).run_inference(test_user, upload.id, save_prediction=True)

    assert response.predicted_label == "apple_pie"
    assert response.matched_food_name == "Apple Pie"
    assert response.food_prediction is not None
    assert [candidate.label for candidate in response.food_prediction.top_k] == ["apple_pie", "sushi", "ramen"]
    assert db_session.scalar(select(func.count()).select_from(PhotoPrediction)) == 1
    saved_prediction = db_session.get(PhotoPrediction, response.saved_prediction_id)
    assert saved_prediction is not None
    assert saved_prediction.predicted_label == "apple_pie"
    assert saved_prediction.predicted_food_item.display_name == "Apple Pie"
    assert db_session.scalar(select(func.count()).select_from(PhotoPredictionCandidate)) == 3


def test_confirmed_cv_prediction_food_log_persists_calories_and_macros(
    monkeypatch: pytest.MonkeyPatch,
    db_session: Session,
    test_user: User,
    tmp_path: Path,
) -> None:
    seed_module.seed_cv_label_food_maps(db_session)
    image_path = create_test_image(tmp_path)
    upload = create_photo_upload(db_session, test_user, image_path)
    result = FullVisionResult(
        binary_prediction=make_binary_result("food", 0.99, "accepted"),
        food_prediction=make_food_result("caesar_salad", 0.95, "accepted"),
    )
    monkeypatch.setattr(
        "app.services.photo_service.get_vision_inference_service",
        lambda: FakeVisionService(result),
    )
    service = PhotoService(db_session)
    response = service.run_inference(test_user, upload.id, save_prediction=True)
    prediction = db_session.get(PhotoPrediction, response.saved_prediction_id)
    assert prediction is not None
    prediction.prediction_status = "confirmed"
    db_session.add(prediction)
    db_session.commit()

    food_log = service.log_prediction_to_food_log(
        current_user=test_user,
        photo_upload_id=upload.id,
        prediction_id=prediction.id,
        payload=PhotoPredictionToFoodLogRequest(
            logged_for_date=date(2026, 5, 10),
            meal_type="lunch",
        ),
    )

    assert food_log.total_calories == 180
    assert food_log.total_protein_g == 5
    assert food_log.total_carbs_g == 7
    assert food_log.total_fat_g == 15
    assert food_log.items[0].calories == 180
    assert food_log.items[0].protein_g == 5
    assert food_log.items[0].carbs_g == 7
    assert food_log.items[0].fat_g == 15
