from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MealType = Literal["breakfast", "lunch", "dinner", "snack"]


class FoodLogItemCreateRequest(BaseModel):
    food_item_id: str
    quantity: float = Field(default=1.0, gt=0, le=100)
    grams: float | None = Field(default=None, gt=0, le=5000)


class FoodLogCreateRequest(BaseModel):
    logged_for_date: date
    meal_type: MealType
    notes: str | None = Field(default=None, max_length=2000)
    items: list[FoodLogItemCreateRequest] = Field(min_length=1)


class FoodLogItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    food_log_id: str
    food_item_id: str

    food_name_snapshot: str
    brand_snapshot: str | None

    quantity: float
    grams: float

    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

    created_at: datetime
    updated_at: datetime


class FoodLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    logged_for_date: date
    meal_type: MealType
    notes: str | None

    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float

    items: list[FoodLogItemResponse]

    created_at: datetime
    updated_at: datetime