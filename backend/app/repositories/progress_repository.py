from __future__ import annotations

from datetime import date

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.progress_snapshot import ProgressSnapshot
from app.models.weight_log import WeightLog
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[ProgressSnapshot]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ProgressSnapshot)

    def get_snapshot_for_user(
        self,
        user_id: str,
        snapshot_id: str,
    ) -> ProgressSnapshot | None:
        return self.db.scalar(
            select(ProgressSnapshot).where(
                ProgressSnapshot.id == snapshot_id,
                ProgressSnapshot.user_id == user_id,
            )
        )

    def get_snapshot_for_user_and_date(
        self,
        user_id: str,
        snapshot_date: date,
    ) -> ProgressSnapshot | None:
        return self.db.scalar(
            select(ProgressSnapshot).where(
                ProgressSnapshot.user_id == user_id,
                ProgressSnapshot.snapshot_date == snapshot_date,
            )
        )

    def list_snapshots_for_user(
        self,
        user_id: str,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> list[ProgressSnapshot]:
        statement = (
            select(ProgressSnapshot)
            .where(ProgressSnapshot.user_id == user_id)
            .order_by(desc(ProgressSnapshot.snapshot_date), desc(ProgressSnapshot.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_latest_weight_on_or_before(
        self,
        user_id: str,
        target_date: date,
    ) -> WeightLog | None:
        return self.db.scalar(
            select(WeightLog)
            .where(
                WeightLog.user_id == user_id,
                WeightLog.logged_for_date <= target_date,
            )
            .order_by(desc(WeightLog.logged_for_date), desc(WeightLog.created_at))
        )

    def list_weight_logs_for_user(
        self,
        user_id: str,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> list[WeightLog]:
        statement = (
            select(WeightLog)
            .where(WeightLog.user_id == user_id)
            .order_by(desc(WeightLog.logged_for_date), desc(WeightLog.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_activity_logs_for_user(
        self,
        user_id: str,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> list[ActivityLog]:
        statement = (
            select(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .order_by(desc(ActivityLog.logged_for_date), desc(ActivityLog.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())