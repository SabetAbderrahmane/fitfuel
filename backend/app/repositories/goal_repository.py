from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.user_goal import UserGoal
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[UserGoal]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, UserGoal)

    def get_active_for_user(self, user_id: str) -> UserGoal | None:
        return self.db.scalar(
            select(UserGoal)
            .where(
                UserGoal.user_id == user_id,
                UserGoal.is_active.is_(True),
            )
            .order_by(desc(UserGoal.started_at))
        )

    def list_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[UserGoal]:
        statement = (
            select(UserGoal)
            .where(UserGoal.user_id == user_id)
            .order_by(desc(UserGoal.started_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())