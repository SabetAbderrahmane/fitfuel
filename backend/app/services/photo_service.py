from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader
import httpx
from fastapi import HTTPException, UploadFile, status
from rapidfuzz import fuzz
from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session, selectinload

from app.ai.vision.preprocessing import load_pil_image_from_bytes
from app.core.config import settings
from app.models.ai_feedback_history import AIFeedbackHistory
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap
from app.models.food_alias import FoodAlias
from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.food_log_item import FoodLogItem
from app.models.photo_prediction import PhotoPrediction
from app.models.photo_prediction_candidate import PhotoPredictionCandidate
from app.models.photo_upload import PhotoUpload
from app.models.user import User
from app.schemas.photo import (
    PhotoPredictionConfirmRequest,
    PhotoPredictionCorrectionRequest,
    PhotoPredictionCreateRequest,
    PhotoPredictionToFoodLogRequest,
    VisionBinaryPredictionResponse,
    VisionFoodPredictionResponse,
    VisionInferenceResponse,
    VisionNutritionEstimateResponse,
    VisionProbabilityResponse,
    VisionTopPredictionResponse,
)
from app.services.vision_inference_service import (
    FoodVisionResult,
    VisionModelUnavailableError,
    VisionPrediction,
    get_vision_inference_service,
)


class PhotoService:
    """
    Handles image ingestion, inference, prediction review, and conversion into logs.

    Batch 3A behavior:
    - resolve classifier labels through classifier_label_food_maps first
    - store candidate rows for manual review
    - require confirm/correct before final log-to-food-log conversion
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _assert_is_image(upload_file: UploadFile) -> None:
        content_type = (upload_file.content_type or "").strip().lower()
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image uploads are supported.",
            )

    @staticmethod
    def _safe_suffix(filename: str | None) -> str:
        if not filename:
            return ".bin"

        suffix = Path(filename).suffix.lower()
        return suffix if suffix else ".bin"

    @staticmethod
    def _ensure_local_upload_dir() -> Path:
        upload_dir = Path(settings.local_upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    @staticmethod
    def _cloudinary_is_configured() -> bool:
        return all(
            [
                settings.cloudinary_cloud_name.strip(),
                settings.cloudinary_api_key.strip(),
                settings.cloudinary_api_secret.strip(),
            ]
        )

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = value.strip().lower()
        normalized = normalized.replace("_", " ").replace("-", " ")
        return " ".join(normalized.split())

    @staticmethod
    def _scale_nutrient(per_100g: float, grams: float) -> float:
        return round((grams / 100.0) * per_100g, 2)

    @staticmethod
    def _prediction_is_reviewed(prediction: PhotoPrediction) -> bool:
        return prediction.prediction_status in {"confirmed", "corrected"}

    def _configure_cloudinary(self) -> None:
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )

    async def upload_photo(
        self,
        current_user: User,
        upload_file: UploadFile,
        notes: str | None = None,
    ) -> PhotoUpload:
        self._assert_is_image(upload_file)

        file_bytes = await upload_file.read()
        file_size_bytes = len(file_bytes)

        max_bytes = settings.max_photo_upload_mb * 1024 * 1024
        if file_size_bytes <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )
        if file_size_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds the {settings.max_photo_upload_mb} MB upload limit.",
            )

        original_filename = upload_file.filename or "upload"
        suffix = self._safe_suffix(original_filename)
        unique_name = f"{uuid4()}{suffix}"

        photo_upload = PhotoUpload(
            user_id=current_user.id,
            original_filename=original_filename,
            content_type=upload_file.content_type or "application/octet-stream",
            file_size_bytes=file_size_bytes,
            storage_provider="local",
            storage_key=unique_name,
            storage_url=None,
            local_file_path=None,
            upload_status="uploaded",
            notes=notes.strip() if notes else None,
        )

        try:
            if self._cloudinary_is_configured():
                self._configure_cloudinary()
                result = cloudinary.uploader.upload(
                    file_bytes,
                    folder="fitfuel/uploads",
                    public_id=Path(unique_name).stem,
                    resource_type="image",
                    overwrite=False,
                )

                photo_upload.storage_provider = "cloudinary"
                photo_upload.storage_key = result["public_id"]
                photo_upload.storage_url = result.get("secure_url")
                photo_upload.local_file_path = None
            else:
                upload_dir = self._ensure_local_upload_dir()
                local_path = upload_dir / unique_name
                local_path.write_bytes(file_bytes)

                photo_upload.storage_provider = "local"
                photo_upload.storage_key = unique_name
                photo_upload.storage_url = None
                photo_upload.local_file_path = str(local_path.resolve())

            self.db.add(photo_upload)
            self.db.commit()
            self.db.refresh(photo_upload)

        except HTTPException:
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Photo upload failed: {str(exc)}",
            ) from exc

        return self.get_photo_upload(
            current_user=current_user,
            photo_upload_id=photo_upload.id,
        )

    def list_photo_uploads(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> list[PhotoUpload]:
        statement: Select[tuple[PhotoUpload]] = (
            select(PhotoUpload)
            .options(selectinload(PhotoUpload.predictions))
            .where(PhotoUpload.user_id == current_user.id)
            .order_by(desc(PhotoUpload.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_photo_upload(
        self,
        current_user: User,
        photo_upload_id: str,
    ) -> PhotoUpload:
        statement = (
            select(PhotoUpload)
            .options(selectinload(PhotoUpload.predictions))
            .where(
                PhotoUpload.id == photo_upload_id,
                PhotoUpload.user_id == current_user.id,
            )
        )
        photo_upload = self.db.scalar(statement)

        if photo_upload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo upload not found.",
            )

        return photo_upload

    def get_local_photo_path(
        self,
        current_user: User,
        photo_upload_id: str,
    ) -> Path:
        photo_upload = self.get_photo_upload(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
        )

        if photo_upload.storage_provider != "local":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This file is not stored locally. Use storage_url instead.",
            )

        if not photo_upload.local_file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Local file path is missing.",
            )

        local_path = Path(photo_upload.local_file_path)
        if not local_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Local file is missing on disk.",
            )

        return local_path

    def _get_photo_bytes(self, photo_upload: PhotoUpload) -> bytes:
        if photo_upload.storage_provider == "local":
            if not photo_upload.local_file_path:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Local file path is missing.",
                )

            local_path = Path(photo_upload.local_file_path)
            if not local_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Local file is missing on disk.",
                )

            return local_path.read_bytes()

        if photo_upload.storage_provider == "cloudinary" and photo_upload.storage_url:
            response = httpx.get(photo_upload.storage_url, timeout=30.0)
            response.raise_for_status()
            return response.content

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve file bytes for this upload.",
        )

    def _get_food_item_with_nutrition(self, food_item_id: str) -> FoodItem:
        statement = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )
        food_item = self.db.scalar(statement)

        if food_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food item not found: {food_item_id}",
            )

        return food_item

    def _get_prediction_owned_by_user(
        self,
        current_user: User,
        photo_upload_id: str,
        prediction_id: str,
    ) -> PhotoPrediction:
        statement = (
            select(PhotoPrediction)
            .join(PhotoUpload, PhotoUpload.id == PhotoPrediction.photo_upload_id)
            .where(
                PhotoPrediction.id == prediction_id,
                PhotoPrediction.photo_upload_id == photo_upload_id,
                PhotoUpload.user_id == current_user.id,
            )
        )
        prediction = self.db.scalar(statement)

        if prediction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo prediction not found.",
            )

        return prediction

    def _calculate_prediction_nutrition(
        self,
        predicted_food_item_id: str | None,
        estimated_grams: float | None,
    ) -> tuple[float | None, float | None, float | None, float | None]:
        if not predicted_food_item_id or estimated_grams is None:
            return None, None, None, None

        food_item = self._get_food_item_with_nutrition(predicted_food_item_id)
        nutrition = food_item.nutrition_fact

        if nutrition is None:
            return None, None, None, None

        estimated_calories = self._scale_nutrient(nutrition.calories_per_100g, estimated_grams)
        estimated_protein_g = self._scale_nutrient(nutrition.protein_g_per_100g, estimated_grams)
        estimated_carbs_g = self._scale_nutrient(nutrition.carbs_g_per_100g, estimated_grams)
        estimated_fat_g = self._scale_nutrient(nutrition.fat_g_per_100g, estimated_grams)

        return (
            estimated_calories,
            estimated_protein_g,
            estimated_carbs_g,
            estimated_fat_g,
        )

    def _build_nutrition_estimate_response(
        self,
        food_item: FoodItem | None,
        serving_grams: float,
    ) -> VisionNutritionEstimateResponse | None:
        if food_item is None or food_item.nutrition_fact is None:
            return None

        nutrition = food_item.nutrition_fact
        return VisionNutritionEstimateResponse(
            food_item_id=food_item.id,
            food_name=food_item.display_name or food_item.name,
            serving_grams=serving_grams,
            estimated_calories=self._scale_nutrient(nutrition.calories_per_100g, serving_grams),
            estimated_protein_g=self._scale_nutrient(nutrition.protein_g_per_100g, serving_grams),
            estimated_carbs_g=self._scale_nutrient(nutrition.carbs_g_per_100g, serving_grams),
            estimated_fat_g=self._scale_nutrient(nutrition.fat_g_per_100g, serving_grams),
        )

    def _find_classifier_label(self, normalized_label: str) -> ClassifierLabel | None:
        statement = select(ClassifierLabel).where(
            ClassifierLabel.normalized_label == normalized_label,
            ClassifierLabel.is_active.is_(True),
        )
        labels = list(self.db.scalars(statement).all())
        for label in labels:
            if label.label_set_name == "food101_subset_resnet50":
                return label
        return labels[0] if labels else None

    def _find_best_food_map_for_classifier_label(
        self,
        classifier_label: ClassifierLabel,
    ) -> ClassifierLabelFoodMap | None:
        statement = (
            select(ClassifierLabelFoodMap)
            .options(selectinload(ClassifierLabelFoodMap.food_item))
            .where(ClassifierLabelFoodMap.classifier_label_id == classifier_label.id)
            .order_by(
                ClassifierLabelFoodMap.ranking.asc(),
                desc(ClassifierLabelFoodMap.match_confidence),
            )
        )
        return self.db.scalar(statement)

    def _find_exact_food_alias(self, normalized_label: str) -> FoodAlias | None:
        statement = (
            select(FoodAlias)
            .options(selectinload(FoodAlias.food_item))
            .join(FoodItem, FoodItem.id == FoodAlias.food_item_id)
            .where(
                FoodAlias.normalized_alias == normalized_label,
                FoodItem.is_active.is_(True),
            )
            .order_by(desc(FoodAlias.confidence_score))
        )
        return self.db.scalar(statement)

    def _match_food_item_by_label(
        self,
        label: str,
        score_threshold: float = 70.0,
    ) -> tuple[
        FoodItem | None,
        float | None,
        str | None,
        ClassifierLabel | None,
        bool,
    ]:
        normalized_label = self._normalize_text(label)
        classifier_label = self._find_classifier_label(normalized_label)

        if classifier_label is not None:
            mapping = self._find_best_food_map_for_classifier_label(classifier_label)
            if mapping is not None and mapping.food_item is not None and mapping.food_item.is_active:
                requires_confirmation = (
                    mapping.requires_user_confirmation
                    or mapping.match_confidence < 0.95
                )
                return (
                    mapping.food_item,
                    round(mapping.match_confidence * 100.0, 2),
                    "classifier_map",
                    classifier_label,
                    requires_confirmation,
                )

        alias = self._find_exact_food_alias(normalized_label)
        if alias is not None and alias.food_item.is_active:
            alias_score = alias.confidence_score
            if alias_score <= 1.0:
                alias_score *= 100.0
            requires_confirmation = alias.alias_type not in {"exact", "source_name"}
            return (
                alias.food_item,
                round(alias_score, 2),
                "alias_exact",
                classifier_label,
                requires_confirmation,
            )

        alias_candidates = list(
            self.db.scalars(
                select(FoodAlias)
                .options(selectinload(FoodAlias.food_item))
                .join(FoodItem, FoodItem.id == FoodAlias.food_item_id)
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodAlias.normalized_alias.asc())
            ).all()
        )

        best_alias: FoodAlias | None = None
        best_alias_score = 0.0

        for alias_candidate in alias_candidates:
            score = float(
                fuzz.token_sort_ratio(
                    normalized_label,
                    self._normalize_text(alias_candidate.normalized_alias),
                )
            )
            if score > best_alias_score:
                best_alias_score = score
                best_alias = alias_candidate

        if best_alias is not None and best_alias_score >= score_threshold:
            return (
                best_alias.food_item,
                round(best_alias_score, 2),
                "fuzzy_alias",
                classifier_label,
                True,
            )

        candidates = list(
            self.db.scalars(
                select(FoodItem)
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.name.asc())
            ).all()
        )

        best_item: FoodItem | None = None
        best_score = 0.0

        for candidate in candidates:
            candidate_names = {
                self._normalize_text(candidate.name),
                self._normalize_text(candidate.display_name or candidate.name),
                self._normalize_text(candidate.normalized_name or candidate.name),
            }

            for candidate_name in candidate_names:
                if not candidate_name:
                    continue
                score = float(fuzz.token_sort_ratio(normalized_label, candidate_name))
                if score > best_score:
                    best_score = score
                    best_item = candidate

        if best_item is None or best_score < score_threshold:
            return None, None, None, classifier_label, True

        return (
            best_item,
            round(best_score, 2),
            "fuzzy_food_item",
            classifier_label,
            True,
        )

    def _build_prediction_candidate_rows(
        self,
        photo_prediction_id: str,
        top_predictions: list,
    ) -> list[PhotoPredictionCandidate]:
        candidate_rows: list[PhotoPredictionCandidate] = []

        for rank, candidate in enumerate(top_predictions, start=1):
            (
                matched_food_item,
                match_score,
                match_strategy,
                classifier_label,
                requires_confirmation,
            ) = self._match_food_item_by_label(candidate.label)

            mapping_confidence: float | None = None
            if match_score is not None:
                mapping_confidence = (
                    round(match_score / 100.0, 4)
                    if match_score > 1.0
                    else round(match_score, 4)
                )

            combined_confidence = round(
                (
                    candidate.confidence_score
                    + (
                        mapping_confidence
                        if mapping_confidence is not None
                        else candidate.confidence_score
                    )
                )
                / 2.0,
                4,
            )

            candidate_rows.append(
                PhotoPredictionCandidate(
                    photo_prediction_id=photo_prediction_id,
                    candidate_rank=rank,
                    classifier_label_id=classifier_label.id if classifier_label else None,
                    food_item_id=matched_food_item.id if matched_food_item else None,
                    vision_confidence=round(candidate.confidence_score, 4),
                    mapping_confidence=mapping_confidence,
                    combined_confidence=combined_confidence,
                    explanation_json={
                        "predicted_label": candidate.label,
                        "match_strategy": match_strategy or "unmapped",
                        "match_score": match_score,
                        "requires_user_confirmation": requires_confirmation,
                    },
                )
            )

        return candidate_rows

    def _build_cv_prediction_candidate_rows(
        self,
        photo_prediction_id: str,
        top_predictions: list[VisionPrediction],
    ) -> list[PhotoPredictionCandidate]:
        candidate_rows: list[PhotoPredictionCandidate] = []

        for rank, candidate in enumerate(top_predictions, start=1):
            (
                matched_food_item,
                match_score,
                match_strategy,
                classifier_label,
                requires_confirmation,
            ) = self._match_food_item_by_label(candidate.label)

            mapping_confidence = None
            if match_score is not None:
                mapping_confidence = round(match_score / 100.0, 4) if match_score > 1.0 else round(match_score, 4)

            combined_confidence = round(
                (
                    candidate.probability
                    + (mapping_confidence if mapping_confidence is not None else candidate.probability)
                )
                / 2.0,
                4,
            )

            candidate_rows.append(
                PhotoPredictionCandidate(
                    photo_prediction_id=photo_prediction_id,
                    candidate_rank=rank,
                    classifier_label_id=classifier_label.id if classifier_label else None,
                    food_item_id=matched_food_item.id if matched_food_item else None,
                    vision_confidence=round(candidate.probability, 4),
                    mapping_confidence=mapping_confidence,
                    combined_confidence=combined_confidence,
                    explanation_json={
                        "predicted_label": candidate.label,
                        "match_strategy": match_strategy or "unmapped",
                        "match_score": match_score,
                        "requires_user_confirmation": requires_confirmation,
                    },
                )
            )

        return candidate_rows

    def add_prediction_result(
        self,
        current_user: User,
        photo_upload_id: str,
        payload: PhotoPredictionCreateRequest,
    ) -> PhotoPrediction:
        photo_upload = self.get_photo_upload(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
        )

        estimated_calories = payload.estimated_calories
        estimated_protein_g = payload.estimated_protein_g
        estimated_carbs_g = payload.estimated_carbs_g
        estimated_fat_g = payload.estimated_fat_g

        resolved_food_item_id = payload.predicted_food_item_id
        normalized_label = self._normalize_text(payload.predicted_label)

        (
            auto_matched_food_item,
            auto_match_score,
            auto_match_strategy,
            classifier_label,
            requires_confirmation,
        ) = self._match_food_item_by_label(payload.predicted_label)

        if resolved_food_item_id is None and auto_matched_food_item is not None:
            resolved_food_item_id = auto_matched_food_item.id

        if resolved_food_item_id and payload.estimated_grams is not None:
            calc = self._calculate_prediction_nutrition(
                predicted_food_item_id=resolved_food_item_id,
                estimated_grams=payload.estimated_grams,
            )
            estimated_calories = estimated_calories if estimated_calories is not None else calc[0]
            estimated_protein_g = estimated_protein_g if estimated_protein_g is not None else calc[1]
            estimated_carbs_g = estimated_carbs_g if estimated_carbs_g is not None else calc[2]
            estimated_fat_g = estimated_fat_g if estimated_fat_g is not None else calc[3]

        note_parts: list[str] = []
        if payload.notes:
            note_parts.append(payload.notes.strip())
        if auto_match_strategy:
            note_parts.append(
                f"Auto-match strategy: {auto_match_strategy} "
                f"(score={auto_match_score})."
            )
        if requires_confirmation:
            note_parts.append("User confirmation is required before logging this prediction.")

        if classifier_label is None:
            classifier_label = self._find_classifier_label(normalized_label)

        prediction = PhotoPrediction(
            photo_upload_id=photo_upload.id,
            predicted_food_item_id=resolved_food_item_id,
            selected_classifier_label_id=classifier_label.id if classifier_label else None,
            model_name=payload.model_name.strip(),
            prediction_status=payload.prediction_status,
            predicted_label=payload.predicted_label.strip(),
            confidence_score=payload.confidence_score,
            estimated_grams=payload.estimated_grams,
            estimated_calories=estimated_calories,
            estimated_protein_g=estimated_protein_g,
            estimated_carbs_g=estimated_carbs_g,
            estimated_fat_g=estimated_fat_g,
            notes=" ".join(note_parts) if note_parts else None,
        )

        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def run_inference(
        self,
        current_user: User,
        photo_upload_id: str,
        top_k: int = 3,
        save_prediction: bool = True,
        serving_grams: float | None = None,
    ) -> VisionInferenceResponse:
        photo_upload = self.get_photo_upload(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
        )

        image_bytes = self._get_photo_bytes(photo_upload)
        pil_image = load_pil_image_from_bytes(image_bytes)

        try:
            inference = get_vision_inference_service().analyze(
                image=pil_image,
                top_k=max(1, min(top_k, 10)),
            )
        except VisionModelUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

        binary = inference.binary_prediction
        food_prediction: FoodVisionResult | None = inference.food_prediction

        matched_food_item: FoodItem | None = None
        match_score: float | None = None
        match_strategy: str | None = None
        classifier_label: ClassifierLabel | None = None
        requires_confirmation = True
        nutrition_estimate: VisionNutritionEstimateResponse | None = None
        mapping_status = "needs_confirmation"

        if food_prediction is not None:
            (
                matched_food_item,
                match_score,
                match_strategy,
                classifier_label,
                requires_confirmation,
            ) = self._match_food_item_by_label(food_prediction.predicted_label)

            effective_serving_grams = serving_grams or settings.vision_default_serving_grams
            nutrition_estimate = self._build_nutrition_estimate_response(
                food_item=matched_food_item,
                serving_grams=effective_serving_grams,
            )

            if matched_food_item is None:
                mapping_status = "unmapped"
            elif food_prediction.user_confirmation_required or requires_confirmation:
                mapping_status = "needs_confirmation"
            else:
                mapping_status = "mapped"
        elif binary.status == "rejected":
            mapping_status = "unmapped"

        saved_prediction_id: str | None = None
        if save_prediction:
            predicted_label = (
                food_prediction.predicted_label
                if food_prediction is not None
                else binary.predicted_label
            )
            confidence_score = (
                food_prediction.confidence
                if food_prediction is not None
                else binary.confidence
            )
            prediction_status = "completed"
            if binary.status == "rejected":
                prediction_status = "rejected"
            elif food_prediction is None or food_prediction.user_confirmation_required or requires_confirmation:
                prediction_status = "pending"

            note_parts = [
                "Auto-generated by FitFuel CV inference.",
                f"Binary gate: label={binary.predicted_label}, food_probability={binary.food_probability}, status={binary.status}.",
                f"Primary match strategy: {match_strategy or 'unmapped'}.",
                f"Mapping status: {mapping_status}.",
            ]
            if binary.message:
                note_parts.append(binary.message)
            if prediction_status == "pending":
                note_parts.append("User confirmation is required before logging this prediction.")

            prediction = PhotoPrediction(
                photo_upload_id=photo_upload.id,
                predicted_food_item_id=matched_food_item.id if matched_food_item else None,
                selected_classifier_label_id=classifier_label.id if classifier_label else None,
                model_name="fitfuel_cv_resnet50_v1",
                prediction_status=prediction_status,
                predicted_label=predicted_label,
                confidence_score=confidence_score,
                estimated_grams=nutrition_estimate.serving_grams if nutrition_estimate else None,
                estimated_calories=nutrition_estimate.estimated_calories if nutrition_estimate else None,
                estimated_protein_g=nutrition_estimate.estimated_protein_g if nutrition_estimate else None,
                estimated_carbs_g=nutrition_estimate.estimated_carbs_g if nutrition_estimate else None,
                estimated_fat_g=nutrition_estimate.estimated_fat_g if nutrition_estimate else None,
                notes=" ".join(note_parts),
                inference_metadata_json={
                    "binary_prediction": {
                        "predicted_label": binary.predicted_label,
                        "food_probability": binary.food_probability,
                        "confidence": binary.confidence,
                        "status": binary.status,
                        "user_confirmation_required": binary.user_confirmation_required,
                    },
                    "food_prediction": (
                        {
                            "predicted_label": food_prediction.predicted_label,
                            "confidence": food_prediction.confidence,
                            "status": food_prediction.status,
                            "user_confirmation_required": food_prediction.user_confirmation_required,
                            "top_k": [
                                {
                                    "label": candidate.label,
                                    "probability": candidate.probability,
                                }
                                for candidate in food_prediction.top_k
                            ],
                        }
                        if food_prediction is not None
                        else None
                    ),
                    "mapping_status": mapping_status,
                    "match_strategy": match_strategy,
                    "match_score": match_score,
                    "serving_grams": nutrition_estimate.serving_grams if nutrition_estimate else None,
                    "thresholds": {
                        "food_accept_threshold": settings.vision_food_accept_threshold,
                        "class_accept_threshold": settings.vision_class_accept_threshold,
                    },
                },
            )
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)

            if food_prediction is not None:
                candidate_rows = self._build_cv_prediction_candidate_rows(
                    photo_prediction_id=prediction.id,
                    top_predictions=food_prediction.top_k,
                )
            else:
                candidate_rows = []

            if candidate_rows:
                self.db.add_all(candidate_rows)
                self.db.commit()

            saved_prediction_id = prediction.id

        top_predictions = []
        if food_prediction is not None:
            top_predictions = [
                VisionTopPredictionResponse(
                    class_index=index,
                    label=candidate.label,
                    confidence_score=candidate.probability,
                )
                for index, candidate in enumerate(food_prediction.top_k)
            ]

        return VisionInferenceResponse(
            photo_upload_id=photo_upload.id,
            model_name="fitfuel_cv_resnet50_v1",
            predicted_label=food_prediction.predicted_label if food_prediction else binary.predicted_label,
            confidence_score=food_prediction.confidence if food_prediction else binary.confidence,
            matched_food_item_id=matched_food_item.id if matched_food_item else None,
            matched_food_name=(
                matched_food_item.display_name or matched_food_item.name
                if matched_food_item
                else None
            ),
            match_score=match_score,
            top_predictions=top_predictions,
            saved_prediction_id=saved_prediction_id,
            binary_prediction=VisionBinaryPredictionResponse(
                predicted_label=binary.predicted_label,
                food_probability=binary.food_probability,
                confidence=binary.confidence,
                status=binary.status,
            ),
            food_prediction=(
                VisionFoodPredictionResponse(
                    predicted_label=food_prediction.predicted_label,
                    confidence=food_prediction.confidence,
                    status=food_prediction.status,
                    user_confirmation_required=food_prediction.user_confirmation_required,
                    top_k=[
                        VisionProbabilityResponse(
                            label=candidate.label,
                            probability=candidate.probability,
                        )
                        for candidate in food_prediction.top_k
                    ],
                )
                if food_prediction is not None
                else None
            ),
            nutrition_estimate=nutrition_estimate,
            mapping_status=mapping_status,
            message=binary.message,
        )

    def list_feedback_history(
        self,
        current_user: User,
        photo_upload_id: str,
    ) -> list[AIFeedbackHistory]:
        self.get_photo_upload(current_user=current_user, photo_upload_id=photo_upload_id)

        statement: Select[tuple[AIFeedbackHistory]] = (
            select(AIFeedbackHistory)
            .where(
                AIFeedbackHistory.user_id == current_user.id,
                AIFeedbackHistory.photo_upload_id == photo_upload_id,
            )
            .order_by(desc(AIFeedbackHistory.created_at))
        )
        return list(self.db.scalars(statement).all())

    def confirm_prediction(
        self,
        current_user: User,
        photo_upload_id: str,
        prediction_id: str,
        payload: PhotoPredictionConfirmRequest,
    ) -> PhotoPrediction:
        prediction = self._get_prediction_owned_by_user(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
            prediction_id=prediction_id,
        )

        if not prediction.predicted_food_item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prediction must be linked to a food item before it can be confirmed.",
            )

        feedback = AIFeedbackHistory(
            user_id=current_user.id,
            photo_upload_id=photo_upload_id,
            photo_prediction_id=prediction.id,
            feedback_type="confirmed",
            original_label=prediction.predicted_label,
            corrected_label=prediction.predicted_label,
            original_food_item_id=prediction.predicted_food_item_id,
            corrected_food_item_id=prediction.predicted_food_item_id,
            original_estimated_grams=prediction.estimated_grams,
            corrected_estimated_grams=prediction.estimated_grams,
            original_estimated_calories=prediction.estimated_calories,
            corrected_estimated_calories=prediction.estimated_calories,
            notes=payload.notes.strip() if payload.notes else None,
        )

        prediction.prediction_status = "confirmed"

        self.db.add(feedback)
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def correct_prediction(
        self,
        current_user: User,
        photo_upload_id: str,
        prediction_id: str,
        payload: PhotoPredictionCorrectionRequest,
    ) -> PhotoPrediction:
        prediction = self._get_prediction_owned_by_user(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
            prediction_id=prediction_id,
        )

        if (
            payload.predicted_label is None
            and payload.predicted_food_item_id is None
            and payload.estimated_grams is None
            and payload.notes is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least one correction field.",
            )

        original_label = prediction.predicted_label
        original_food_item_id = prediction.predicted_food_item_id
        original_estimated_grams = prediction.estimated_grams
        original_estimated_calories = prediction.estimated_calories

        new_label = prediction.predicted_label
        if payload.predicted_label is not None:
            new_label = payload.predicted_label.strip()

        new_food_item_id = prediction.predicted_food_item_id
        auto_matched_food_item: FoodItem | None = None
        classifier_label: ClassifierLabel | None = None

        if payload.predicted_food_item_id is not None:
            new_food_item_id = payload.predicted_food_item_id
            matched_food = self._get_food_item_with_nutrition(payload.predicted_food_item_id)
            if payload.predicted_label is None:
                new_label = matched_food.display_name or matched_food.name
            classifier_label = self._find_classifier_label(self._normalize_text(new_label))
        elif payload.predicted_label is not None:
            (
                auto_matched_food_item,
                _auto_match_score,
                _auto_match_strategy,
                classifier_label,
                _requires_confirmation,
            ) = self._match_food_item_by_label(new_label)
            if auto_matched_food_item is not None:
                new_food_item_id = auto_matched_food_item.id

        new_estimated_grams = (
            payload.estimated_grams
            if payload.estimated_grams is not None
            else prediction.estimated_grams
        )

        if classifier_label is None:
            classifier_label = self._find_classifier_label(self._normalize_text(new_label))

        calc = self._calculate_prediction_nutrition(
            predicted_food_item_id=new_food_item_id,
            estimated_grams=new_estimated_grams,
        )

        prediction.predicted_label = new_label
        prediction.predicted_food_item_id = new_food_item_id
        prediction.selected_classifier_label_id = (
            classifier_label.id if classifier_label else None
        )
        prediction.estimated_grams = new_estimated_grams
        prediction.estimated_calories = calc[0]
        prediction.estimated_protein_g = calc[1]
        prediction.estimated_carbs_g = calc[2]
        prediction.estimated_fat_g = calc[3]
        prediction.prediction_status = "corrected"

        if payload.notes is not None:
            prediction.notes = payload.notes.strip() if payload.notes else None

        feedback = AIFeedbackHistory(
            user_id=current_user.id,
            photo_upload_id=photo_upload_id,
            photo_prediction_id=prediction.id,
            feedback_type="corrected",
            original_label=original_label,
            corrected_label=prediction.predicted_label,
            original_food_item_id=original_food_item_id,
            corrected_food_item_id=prediction.predicted_food_item_id,
            original_estimated_grams=original_estimated_grams,
            corrected_estimated_grams=prediction.estimated_grams,
            original_estimated_calories=original_estimated_calories,
            corrected_estimated_calories=prediction.estimated_calories,
            notes=payload.notes.strip() if payload.notes else None,
        )

        self.db.add(feedback)
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def log_prediction_to_food_log(
        self,
        current_user: User,
        photo_upload_id: str,
        prediction_id: str,
        payload: PhotoPredictionToFoodLogRequest,
    ) -> FoodLog:
        prediction = self._get_prediction_owned_by_user(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
            prediction_id=prediction_id,
        )

        if not self._prediction_is_reviewed(prediction):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prediction must be confirmed or corrected before logging to food log.",
            )

        if not prediction.predicted_food_item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prediction must be linked to a food item before logging.",
            )

        if prediction.estimated_grams is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prediction must have estimated grams before logging.",
            )

        food_item = self._get_food_item_with_nutrition(prediction.predicted_food_item_id)
        nutrition = food_item.nutrition_fact

        if nutrition is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Linked food item has no nutrition facts.",
            )

        calories = (
            prediction.estimated_calories
            if prediction.estimated_calories is not None
            else self._scale_nutrient(nutrition.calories_per_100g, prediction.estimated_grams)
        )
        protein_g = (
            prediction.estimated_protein_g
            if prediction.estimated_protein_g is not None
            else self._scale_nutrient(nutrition.protein_g_per_100g, prediction.estimated_grams)
        )
        carbs_g = (
            prediction.estimated_carbs_g
            if prediction.estimated_carbs_g is not None
            else self._scale_nutrient(nutrition.carbs_g_per_100g, prediction.estimated_grams)
        )
        fat_g = (
            prediction.estimated_fat_g
            if prediction.estimated_fat_g is not None
            else self._scale_nutrient(nutrition.fat_g_per_100g, prediction.estimated_grams)
        )

        food_log = FoodLog(
            user_id=current_user.id,
            logged_for_date=payload.logged_for_date,
            meal_type=payload.meal_type,
            source_type="photo",
            notes=payload.notes.strip() if payload.notes else f"Logged from photo upload {photo_upload_id}",
            total_calories=round(calories, 2),
            total_protein_g=round(protein_g, 2),
            total_carbs_g=round(carbs_g, 2),
            total_fat_g=round(fat_g, 2),
        )

        log_item = FoodLogItem(
            food_item_id=food_item.id,
            photo_prediction_id=prediction.id,
            food_name_snapshot=food_item.display_name or food_item.name,
            brand_snapshot=food_item.brand,
            serving_name=food_item.default_serving_label or "estimated portion",
            source_snapshot={
                "source_type": "photo",
                "photo_upload_id": photo_upload_id,
                "photo_prediction_id": prediction.id,
                "prediction_status": prediction.prediction_status,
                "predicted_label": prediction.predicted_label,
                "catalog_food_item_id": food_item.id,
            },
            quantity=1.0,
            grams=round(prediction.estimated_grams, 2),
            calories=round(calories, 2),
            protein_g=round(protein_g, 2),
            carbs_g=round(carbs_g, 2),
            fat_g=round(fat_g, 2),
        )
        food_log.items.append(log_item)
        food_item.usage_count = int(food_item.usage_count or 0) + 1

        self.db.add(food_log)
        self.db.commit()
        self.db.refresh(food_log)

        return food_log
