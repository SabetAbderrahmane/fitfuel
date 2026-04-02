from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GroceryListGenerateFromMealPlanRequest(BaseModel):
    meal_plan_id: str
    list_date: date
    title: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)


class GroceryListItemUpdateRequest(BaseModel):
    is_checked: bool


class GroceryListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    grocery_list_id: str
    food_item_id: str | None
    position: int

    item_name_snapshot: str
    category_snapshot: str | None
    total_grams: float | None
    quantity_label: str | None
    is_checked: bool

    created_at: datetime
    updated_at: datetime


class GroceryListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    meal_plan_id: str | None

    title: str
    list_date: date
    source_type: str
    status: str
    notes: str | None

    item_count: int
    items: list[GroceryListItemResponse]

    created_at: datetime
    updated_at: datetime