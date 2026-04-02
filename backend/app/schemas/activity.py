from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityLogCreateRequest(BaseModel):
    logged_for_date: date
    activity_type: str = Field(min_length=1, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=0, le=1440)
    calories_burned: float | None = Field(default=None, ge=0, le=20000)
    intensity: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    logged_for_date: date
    activity_type: str
    duration_minutes: int | None
    calories_burned: float | None
    intensity: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime