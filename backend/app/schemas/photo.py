from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PhotoLogMealType = Literal["breakfast", "lunch", "dinner", "snack"]
PredictionStatus = Literal[
    "pending",
    "completed",
    "failed",
    "confirmed",
    "corrected",
    "rejected",
]


class PhotoPredictionCreateRequest(BaseModel):
    predicted_label: str = Field(min_length=1, max_length=255)
    predicted_food_item_id: str | None = None

    model_name: str = Field(default="manual_placeholder", max_length=100)
    prediction_status: PredictionStatus = "completed"
    confidence_score: float | None = Field(default=None, ge=0, le=1)

    estimated_grams: float | None = Field(default=None, ge=0, le=10000)
    estimated_calories: float | None = Field(default=None, ge=0, le=50000)
    estimated_protein_g: float | None = Field(default=None, ge=0, le=5000)
    estimated_carbs_g: float | None = Field(default=None, ge=0, le=5000)
    estimated_fat_g: float | None = Field(default=None, ge=0, le=5000)

    notes: str | None = Field(default=None, max_length=2000)


class PhotoPredictionConfirmRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class PhotoPredictionCorrectionRequest(BaseModel):
    predicted_label: str | None = Field(default=None, max_length=255)
    predicted_food_item_id: str | None = None
    estimated_grams: float | None = Field(default=None, ge=0, le=10000)
    notes: str | None = Field(default=None, max_length=2000)


class PhotoPredictionToFoodLogRequest(BaseModel):
    logged_for_date: date
    meal_type: PhotoLogMealType
    notes: str | None = Field(default=None, max_length=2000)


class PhotoPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    photo_upload_id: str
    predicted_food_item_id: str | None

    model_name: str
    prediction_status: PredictionStatus
    predicted_label: str
    confidence_score: float | None

    estimated_grams: float | None
    estimated_calories: float | None
    estimated_protein_g: float | None
    estimated_carbs_g: float | None
    estimated_fat_g: float | None

    notes: str | None
    inference_metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class AIFeedbackHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    photo_upload_id: str
    photo_prediction_id: str

    feedback_type: str

    original_label: str
    corrected_label: str

    original_food_item_id: str | None
    corrected_food_item_id: str | None

    original_estimated_grams: float | None
    corrected_estimated_grams: float | None

    original_estimated_calories: float | None
    corrected_estimated_calories: float | None

    notes: str | None
    created_at: datetime
    updated_at: datetime


class PhotoUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    original_filename: str
    content_type: str
    file_size_bytes: int

    storage_provider: str
    storage_key: str
    storage_url: str | None
    local_file_path: str | None

    upload_status: str
    notes: str | None

    predictions: list[PhotoPredictionResponse]

    created_at: datetime
    updated_at: datetime


class VisionTopPredictionResponse(BaseModel):
    class_index: int
    label: str
    confidence_score: float


class VisionProbabilityResponse(BaseModel):
    label: str
    probability: float


class VisionBinaryPredictionResponse(BaseModel):
    predicted_label: str
    food_probability: float
    confidence: float
    status: Literal["accepted", "rejected", "uncertain"]


class VisionFoodPredictionResponse(BaseModel):
    predicted_label: str
    confidence: float
    status: Literal["accepted", "uncertain"]
    user_confirmation_required: bool
    top_k: list[VisionProbabilityResponse]


class VisionNutritionEstimateResponse(BaseModel):
    food_item_id: str
    food_name: str
    serving_grams: float
    estimated_calories: float
    estimated_protein_g: float
    estimated_carbs_g: float
    estimated_fat_g: float


class VisionInferenceResponse(BaseModel):
    photo_upload_id: str
    model_name: str | None = None

    predicted_label: str | None = None
    confidence_score: float | None = None

    matched_food_item_id: str | None
    matched_food_name: str | None
    match_score: float | None

    top_predictions: list[VisionTopPredictionResponse]
    saved_prediction_id: str | None

    binary_prediction: VisionBinaryPredictionResponse | None = None
    food_prediction: VisionFoodPredictionResponse | None = None
    nutrition_estimate: VisionNutritionEstimateResponse | None = None
    mapping_status: Literal["mapped", "unmapped", "needs_confirmation"] | None = None
    message: str | None = None
