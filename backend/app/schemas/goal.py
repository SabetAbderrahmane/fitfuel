from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GoalType = Literal["weight_loss", "maintenance", "muscle_gain", "weight_gain"]
CalculationMode = Literal["calculated", "manual"]
BMRFormula = Literal["mifflin_st_jeor", "harris_benedict"]


class UserGoalCreateRequest(BaseModel):
    goal_type: GoalType
    notes: str | None = Field(default=None, max_length=1000)

    calculation_mode: CalculationMode = "calculated"
    bmr_formula: BMRFormula = "mifflin_st_jeor"

    target_weight_kg: float | None = Field(default=None, ge=20, le=500)
    weekly_target_rate_kg: float | None = Field(default=None, ge=0.05, le=2.0)

    # Used only in manual mode
    target_calories: int | None = Field(default=None, ge=800, le=10000)
    target_protein_g: int | None = Field(default=None, ge=0, le=1000)
    target_carbs_g: int | None = Field(default=None, ge=0, le=1500)
    target_fat_g: int | None = Field(default=None, ge=0, le=500)


class UserGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    goal_type: GoalType
    notes: str | None

    calculation_mode: CalculationMode
    bmr_formula: BMRFormula | None
    estimated_bmr: float | None
    estimated_tdee: float | None

    target_weight_kg: float | None
    weekly_target_rate_kg: float | None

    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int

    is_active: bool
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime