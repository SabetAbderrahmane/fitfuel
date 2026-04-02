from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


PreferenceType = Literal["diet_type", "disliked_food", "preferred_food", "restriction"]


class UserAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool


class ActivityProfileUpsertRequest(BaseModel):
    activity_level: str | None = Field(default=None, max_length=50)
    workout_days_per_week: int | None = Field(default=None, ge=0, le=14)
    preferred_workout_style: str | None = Field(default=None, max_length=100)
    daily_step_goal: int | None = Field(default=None, ge=0, le=100000)
    notes: str | None = Field(default=None, max_length=2000)


class AllergyUpsertRequest(BaseModel):
    allergen_name: str = Field(min_length=1, max_length=100)
    severity: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=1000)
    is_active: bool = True


class DietaryPreferenceUpsertRequest(BaseModel):
    preference_type: PreferenceType
    value: str = Field(min_length=1, max_length=255)
    notes: str | None = Field(default=None, max_length=1000)
    is_active: bool = True


class UserProfileUpsertRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)

    age: int | None = Field(default=None, ge=10, le=120)
    sex: str | None = Field(default=None, max_length=20)

    height_cm: float | None = Field(default=None, ge=50, le=300)
    start_weight_kg: float | None = Field(default=None, ge=20, le=500)
    current_weight_kg: float | None = Field(default=None, ge=20, le=500)

    activity_profile: ActivityProfileUpsertRequest | None = None
    allergies: list[AllergyUpsertRequest] = Field(default_factory=list)
    dietary_preferences: list[DietaryPreferenceUpsertRequest] = Field(default_factory=list)


class ActivityProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    activity_level: str | None
    workout_days_per_week: int | None
    preferred_workout_style: str | None
    daily_step_goal: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AllergyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    allergen_name: str
    severity: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DietaryPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    preference_type: PreferenceType
    value: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


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

    activity_profile: ActivityProfileResponse | None
    allergies: list[AllergyResponse]
    dietary_preferences: list[DietaryPreferenceResponse]

    created_at: datetime
    updated_at: datetime