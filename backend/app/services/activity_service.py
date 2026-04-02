from __future__ import annotations

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityLogCreateRequest


class ActivityService:
    """
    Handles activity log CRUD for the current phase.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_activity_log(
        self,
        current_user: User,
        payload: ActivityLogCreateRequest,
    ) -> ActivityLog:
        activity_log = ActivityLog(
            user_id=current_user.id,
            logged_for_date=payload.logged_for_date,
            activity_type=payload.activity_type.strip(),
            duration_minutes=payload.duration_minutes,
            calories_burned=payload.calories_burned,
            intensity=payload.intensity.strip() if payload.intensity else None,
            notes=payload.notes.strip() if payload.notes else None,
        )

        self.db.add(activity_log)
        self.db.commit()
        self.db.refresh(activity_log)

        return activity_log

    def list_activity_logs(
        self,
        current_user: User,
        limit: int = 30,
        offset: int = 0,
    ) -> list[ActivityLog]:
        statement: Select[tuple[ActivityLog]] = (
            select(ActivityLog)
            .where(ActivityLog.user_id == current_user.id)
            .order_by(desc(ActivityLog.logged_for_date), desc(ActivityLog.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())