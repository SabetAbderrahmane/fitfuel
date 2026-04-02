from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool


class UserProfileUpsertRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)

    age: int | None = Field(default=None, ge=10, le=120)
    sex: str | None = Field(default=None, max_length=20)

    height_cm: float | None = Field(default=None, ge=50, le=300)
    start_weight_kg: float | None = Field(default=None, ge=20, le=500)
    current_weight_kg: float | None = Field(default=None, ge=20, le=500)

    activity_level: str | None = Field(default=None, max_length=50)
    diet_type: str | None = Field(default=None, max_length=50)

    allergies: list[str] = Field(default_factory=list)
    disliked_foods: list[str] = Field(default_factory=list)


class UserProfileResponse(BaseModel):
    id: str
    user_id: str

    first_name: str | None
    last_name: str | None

    age: int | None
    sex: str | None

    height_cm: float | None
    start_weight_kg: float | None
    current_weight_kg: float | None

    activity_level: str | None
    diet_type: str | None

    allergies: list[str]
    disliked_foods: list[str]

    created_at: datetime
    updated_at: datetime