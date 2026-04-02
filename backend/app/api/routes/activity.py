from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.activity import ActivityLogCreateRequest, ActivityLogResponse
from app.services.activity_service import ActivityService
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post(
    "/logs",
    response_model=ActivityLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an activity log entry",
)
async def create_activity_log(
    payload: ActivityLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityLogResponse:
    service = ActivityService(db)
    log = service.create_activity_log(current_user=current_user, payload=payload)
    return ActivityLogResponse.model_validate(log)


@router.get(
    "/logs",
    response_model=list[ActivityLogResponse],
    summary="List current user's activity logs",
)
async def list_activity_logs(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActivityLogResponse]:
    service = ActivityService(db)
    logs = service.list_activity_logs(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [ActivityLogResponse.model_validate(log) for log in logs]