from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WeightLogCreateRequest(BaseModel):
    logged_for_date: date
    weight_kg: float = Field(gt=0, le=1000)
    notes: str | None = Field(default=None, max_length=2000)


class WeightLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    logged_for_date: date
    weight_kg: float
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ProgressSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    snapshot_date: date

    current_weight_kg: float | None
    target_weight_kg: float | None

    consumed_calories: float
    consumed_protein_g: float
    consumed_carbs_g: float
    consumed_fat_g: float

    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int

    calorie_adherence_pct: float
    protein_adherence_pct: float
    carbs_adherence_pct: float
    fat_adherence_pct: float
    overall_adherence_score: float

    created_at: datetime
    updated_at: datetime