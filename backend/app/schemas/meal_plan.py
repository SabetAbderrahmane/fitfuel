from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MealSlot = Literal["breakfast", "lunch", "dinner", "snack"]
GenerationMode = Literal["manual", "rule_based"]


class MealPlanItemCreateRequest(BaseModel):
    food_item_id: str
    meal_slot: MealSlot
    planned_quantity: float = Field(default=1.0, gt=0, le=100)
    planned_grams: float | None = Field(default=None, gt=0, le=5000)
    notes: str | None = Field(default=None, max_length=1000)


class MealPlanCreateRequest(BaseModel):
    plan_date: date
    notes: str | None = Field(default=None, max_length=2000)
    items: list[MealPlanItemCreateRequest] = Field(min_length=1)


class MealPlanGenerateRequest(BaseModel):
    plan_date: date
    notes: str | None = Field(default=None, max_length=2000)
    meal_slots: list[MealSlot] = Field(
        default_factory=lambda: ["breakfast", "lunch", "dinner", "snack"],
        min_length=1,
    )
    preferred_food_item_ids: list[str] = Field(default_factory=list)
    max_items_per_slot: int = Field(default=1, ge=1, le=3)


class MealPlanItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meal_plan_id: str
    food_item_id: str

    meal_slot: MealSlot
    position: int

    food_name_snapshot: str
    brand_snapshot: str | None

    planned_quantity: float
    planned_grams: float

    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

    notes: str | None
    created_at: datetime
    updated_at: datetime


class MealPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    goal_id: str | None
    plan_date: date
    generation_mode: GenerationMode
    notes: str | None

    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    item_count: int

    items: list[MealPlanItemResponse]

    created_at: datetime
    updated_at: datetime