from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientCreateRequest(BaseModel):
    food_item_id: str
    grams: float = Field(gt=0, le=10000)
    quantity_label: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class RecipeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    instructions: str | None = Field(default=None, max_length=20000)

    prep_time_minutes: int | None = Field(default=None, ge=0, le=1440)
    cook_time_minutes: int | None = Field(default=None, ge=0, le=1440)
    servings: int = Field(default=1, ge=1, le=100)

    category: str | None = Field(default=None, max_length=100)
    diet_type: str | None = Field(default=None, max_length=50)
    source: str = Field(default="manual", max_length=50)

    ingredients: list[RecipeIngredientCreateRequest] = Field(min_length=1)


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipe_id: str
    food_item_id: str
    position: int

    ingredient_name_snapshot: str
    quantity_label: str | None
    grams: float
    notes: str | None

    created_at: datetime
    updated_at: datetime


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_user_id: str | None

    name: str
    slug: str
    description: str | None
    instructions: str | None

    prep_time_minutes: int | None
    cook_time_minutes: int | None
    servings: int

    category: str | None
    diet_type: str | None
    source: str
    is_active: bool

    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float

    ingredients: list[RecipeIngredientResponse]

    created_at: datetime
    updated_at: datetime