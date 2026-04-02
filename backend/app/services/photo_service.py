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
from app.ai.vision.vision_classifier import get_vision_classifier
from app.core.config import settings
from app.models.ai_feedback_history import AIFeedbackHistory
from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.food_log_item import FoodLogItem
from app.models.photo_prediction import PhotoPrediction
from app.models.photo_upload import PhotoUpload
from app.models.user import User
from app.schemas.photo import (
    AIFeedbackHistoryResponse,
    PhotoPredictionConfirmRequest,
    PhotoPredictionCorrectionRequest,
    PhotoPredictionCreateRequest,
    PhotoPredictionToFoodLogRequest,
    VisionInferenceResponse,
    VisionTopPredictionResponse,
)


class PhotoService:
    """
    Handles image ingestion, inference, prediction review, and conversion into logs.
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

    @staticmethod
    def _scale_nutrient(per_100g: float, grams: float) -> float:
        return round((grams / 100.0) * per_100g, 2)

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

    def _match_food_item_by_label(
        self,
        label: str,
        score_threshold: float = 70.0,
    ) -> tuple[FoodItem | None, float | None]:
        candidates = list(
            self.db.scalars(
                select(FoodItem)
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.name.asc())
            ).all()
        )

        if not candidates:
            return None, None

        best_item: FoodItem | None = None
        best_score = 0.0

        for candidate in candidates:
            score = float(fuzz.token_sort_ratio(label.lower(), candidate.name.lower()))
            if score > best_score:
                best_score = score
                best_item = candidate

        if best_item is None or best_score < score_threshold:
            return None, None

        return best_item, round(best_score, 2)

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

        if payload.predicted_food_item_id and payload.estimated_grams is not None:
            calc = self._calculate_prediction_nutrition(
                predicted_food_item_id=payload.predicted_food_item_id,
                estimated_grams=payload.estimated_grams,
            )
            estimated_calories = estimated_calories if estimated_calories is not None else calc[0]
            estimated_protein_g = estimated_protein_g if estimated_protein_g is not None else calc[1]
            estimated_carbs_g = estimated_carbs_g if estimated_carbs_g is not None else calc[2]
            estimated_fat_g = estimated_fat_g if estimated_fat_g is not None else calc[3]

        prediction = PhotoPrediction(
            photo_upload_id=photo_upload.id,
            predicted_food_item_id=payload.predicted_food_item_id,
            model_name=payload.model_name.strip(),
            prediction_status=payload.prediction_status.strip(),
            predicted_label=payload.predicted_label.strip(),
            confidence_score=payload.confidence_score,
            estimated_grams=payload.estimated_grams,
            estimated_calories=estimated_calories,
            estimated_protein_g=estimated_protein_g,
            estimated_carbs_g=estimated_carbs_g,
            estimated_fat_g=estimated_fat_g,
            notes=payload.notes.strip() if payload.notes else None,
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
    ) -> VisionInferenceResponse:
        photo_upload = self.get_photo_upload(
            current_user=current_user,
            photo_upload_id=photo_upload_id,
        )

        image_bytes = self._get_photo_bytes(photo_upload)
        pil_image = load_pil_image_from_bytes(image_bytes)

        classifier = get_vision_classifier()
        inference = classifier.infer_pil_image(
            image=pil_image,
            top_k=max(1, min(top_k, 10)),
        )

        matched_food_item, match_score = self._match_food_item_by_label(
            inference.predicted_label
        )

        saved_prediction_id: str | None = None
        if save_prediction:
            prediction = PhotoPrediction(
                photo_upload_id=photo_upload.id,
                predicted_food_item_id=matched_food_item.id if matched_food_item else None,
                model_name=inference.model_name,
                prediction_status="completed",
                predicted_label=inference.predicted_label,
                confidence_score=inference.confidence_score,
                estimated_grams=None,
                estimated_calories=None,
                estimated_protein_g=None,
                estimated_carbs_g=None,
                estimated_fat_g=None,
                notes=(
                    "Auto-generated by vision inference skeleton. "
                    "Top predictions: "
                    + ", ".join(
                        f"{candidate.label} ({candidate.confidence_score:.4f})"
                        for candidate in inference.top_predictions
                    )
                ),
            )
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            saved_prediction_id = prediction.id

        return VisionInferenceResponse(
            photo_upload_id=photo_upload.id,
            model_name=inference.model_name,
            predicted_label=inference.predicted_label,
            confidence_score=inference.confidence_score,
            matched_food_item_id=matched_food_item.id if matched_food_item else None,
            matched_food_name=matched_food_item.name if matched_food_item else None,
            match_score=match_score,
            top_predictions=[
                VisionTopPredictionResponse(
                    class_index=candidate.class_index,
                    label=candidate.label,
                    confidence_score=candidate.confidence_score,
                )
                for candidate in inference.top_predictions
            ],
            saved_prediction_id=saved_prediction_id,
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

        new_food_item_id = (
            payload.predicted_food_item_id
            if payload.predicted_food_item_id is not None
            else prediction.predicted_food_item_id
        )

        new_estimated_grams = (
            payload.estimated_grams
            if payload.estimated_grams is not None
            else prediction.estimated_grams
        )

        new_label = prediction.predicted_label
        if payload.predicted_label is not None:
            new_label = payload.predicted_label.strip()

        if payload.predicted_food_item_id is not None and payload.predicted_label is None:
            matched_food = self._get_food_item_with_nutrition(payload.predicted_food_item_id)
            new_label = matched_food.name

        calc = self._calculate_prediction_nutrition(
            predicted_food_item_id=new_food_item_id,
            estimated_grams=new_estimated_grams,
        )

        prediction.predicted_label = new_label
        prediction.predicted_food_item_id = new_food_item_id
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
            notes=payload.notes.strip() if payload.notes else f"Logged from photo upload {photo_upload_id}",
            total_calories=round(calories, 2),
            total_protein_g=round(protein_g, 2),
            total_carbs_g=round(carbs_g, 2),
            total_fat_g=round(fat_g, 2),
        )

        log_item = FoodLogItem(
            food_item_id=food_item.id,
            food_name_snapshot=food_item.name,
            brand_snapshot=food_item.brand,
            quantity=1.0,
            grams=round(prediction.estimated_grams, 2),
            calories=round(calories, 2),
            protein_g=round(protein_g, 2),
            carbs_g=round(carbs_g, 2),
            fat_g=round(fat_g, 2),
        )
        food_log.items.append(log_item)

        self.db.add(food_log)
        self.db.commit()
        self.db.refresh(food_log)

        return food_log