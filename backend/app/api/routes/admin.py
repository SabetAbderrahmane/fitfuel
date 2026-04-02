from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.admin import (
    AdminOverviewResponse,
    AuditLogResponse,
    FailedLoginAttemptResponse,
)
from app.services.admin_service import AdminService
from app.services.auth_service import get_current_admin

router = APIRouter()


@router.get(
    "/overview",
    response_model=AdminOverviewResponse,
    summary="Get admin overview metrics",
)
async def get_admin_overview(
    _admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminOverviewResponse:
    service = AdminService(db)
    return AdminOverviewResponse(**service.get_overview())


@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
    summary="List recent audit logs",
)
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    service = AdminService(db)
    logs = service.list_audit_logs(limit=limit, offset=offset)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get(
    "/failed-logins",
    response_model=list[FailedLoginAttemptResponse],
    summary="List recent failed login attempts",
)
async def list_failed_logins(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[FailedLoginAttemptResponse]:
    service = AdminService(db)
    attempts = service.list_failed_login_attempts(limit=limit, offset=offset)
    return [FailedLoginAttemptResponse.model_validate(item) for item in attempts]