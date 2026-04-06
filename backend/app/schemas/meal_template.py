from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MealTemplateSlot = Literal["breakfast", "lunch", "dinner", "snack"]


class MealTemplateCreateRequest(BaseModel):
    recipe_id: str | None = None
    name: str | None = Field(default=None, max_length=255)

    meal_slot: MealTemplateSlot | None = None
    category: str | None = Field(default=None, max_length=100)
    diet_type: str | None = Field(default=None, max_length=50)
    source: str = Field(default="manual", max_length=50)
    description: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)

    estimated_calories: float | None = Field(default=None, ge=0, le=50000)
    estimated_protein_g: float | None = Field(default=None, ge=0, le=5000)
    estimated_carbs_g: float | None = Field(default=None, ge=0, le=5000)
    estimated_fat_g: float | None = Field(default=None, ge=0, le=5000)


class MealTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_user_id: str | None
    recipe_id: str | None

    name: str
    slug: str
    meal_slot: str | None
    category: str | None
    diet_type: str | None
    source: str
    description: str | None
    notes: str | None

    estimated_calories: float | None
    estimated_protein_g: float | None
    estimated_carbs_g: float | None
    estimated_fat_g: float | None

    is_active: bool
    created_at: datetime
    updated_at: datetime