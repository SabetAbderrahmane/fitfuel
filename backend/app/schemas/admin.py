from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    action: str
    entity_type: str | None
    entity_id: str | None
    ip_address: str | None
    user_agent: str | None
    details_json: str | None
    created_at: datetime
    updated_at: datetime


class FailedLoginAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    ip_address: str | None
    user_agent: str | None
    failure_reason: str
    created_at: datetime
    updated_at: datetime


class AdminOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    total_refresh_tokens: int
    active_refresh_tokens: int
    recent_failed_logins: int
    recent_audit_events: int