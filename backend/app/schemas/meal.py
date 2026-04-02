from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NutritionFactCreateRequest(BaseModel):
    calories_per_100g: float = Field(ge=0, le=2000)
    protein_g_per_100g: float = Field(ge=0, le=1000)
    carbs_g_per_100g: float = Field(ge=0, le=1000)
    fat_g_per_100g: float = Field(ge=0, le=1000)

    fiber_g_per_100g: float | None = Field(default=None, ge=0, le=1000)
    sugar_g_per_100g: float | None = Field(default=None, ge=0, le=1000)
    sodium_mg_per_100g: float | None = Field(default=None, ge=0, le=100000)


class NutritionFactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    food_item_id: str

    calories_per_100g: float
    protein_g_per_100g: float
    carbs_g_per_100g: float
    fat_g_per_100g: float

    fiber_g_per_100g: float | None
    sugar_g_per_100g: float | None
    sodium_mg_per_100g: float | None

    created_at: datetime
    updated_at: datetime


class FoodItemCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

    default_serving_size_g: float | None = Field(default=None, ge=0, le=5000)
    default_serving_label: str | None = Field(default=None, max_length=100)

    source: str = Field(default="manual", max_length=50)
    nutrition: NutritionFactCreateRequest


class FoodItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    brand: str | None
    category: str | None
    description: str | None
    default_serving_size_g: float | None
    default_serving_label: str | None
    source: str
    is_active: bool

    nutrition_fact: NutritionFactResponse | None

    created_at: datetime
    updated_at: datetime