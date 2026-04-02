from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.progress import (
    ProgressSnapshotResponse,
    WeightLogCreateRequest,
    WeightLogResponse,
)
from app.services.auth_service import get_current_user
from app.services.progress_service import ProgressService

router = APIRouter()


@router.post(
    "/weight-logs",
    response_model=WeightLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a weight log entry",
)
async def create_weight_log(
    payload: WeightLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WeightLogResponse:
    service = ProgressService(db)
    weight_log = service.create_weight_log(current_user=current_user, payload=payload)
    return WeightLogResponse.model_validate(weight_log)


@router.get(
    "/weight-logs",
    response_model=list[WeightLogResponse],
    summary="List current user's weight logs",
)
async def list_weight_logs(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WeightLogResponse]:
    service = ProgressService(db)
    logs = service.list_weight_logs(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [WeightLogResponse.model_validate(log) for log in logs]


@router.post(
    "/snapshots/generate",
    response_model=ProgressSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate or refresh a daily progress snapshot",
)
async def generate_snapshot(
    snapshot_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressSnapshotResponse:
    service = ProgressService(db)
    snapshot = service.generate_daily_snapshot(
        current_user=current_user,
        snapshot_date=snapshot_date,
    )
    return ProgressSnapshotResponse.model_validate(snapshot)


@router.get(
    "/snapshots",
    response_model=list[ProgressSnapshotResponse],
    summary="List progress snapshots",
)
async def list_progress_snapshots(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProgressSnapshotResponse]:
    service = ProgressService(db)
    snapshots = service.list_progress_snapshots(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [ProgressSnapshotResponse.model_validate(snapshot) for snapshot in snapshots]


@router.get(
    "/snapshots/{snapshot_id}",
    response_model=ProgressSnapshotResponse,
    summary="Get one progress snapshot",
)
async def get_progress_snapshot(
    snapshot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressSnapshotResponse:
    service = ProgressService(db)
    snapshot = service.get_progress_snapshot(
        current_user=current_user,
        snapshot_id=snapshot_id,
    )
    return ProgressSnapshotResponse.model_validate(snapshot)