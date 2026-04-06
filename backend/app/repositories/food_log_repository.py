from __future__ import annotations

from datetime import date

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_log import FoodLog
from app.repositories.base import BaseRepository


class FoodLogRepository(BaseRepository[FoodLog]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, FoodLog)

    def get_for_user(self, user_id: str, food_log_id: str) -> FoodLog | None:
        return self.db.scalar(
            select(FoodLog)
            .options(selectinload(FoodLog.items))
            .where(
                FoodLog.id == food_log_id,
                FoodLog.user_id == user_id,
            )
        )

    def list_for_user(
        self,
        user_id: str,
        *,
        logged_for_date: date | None = None,
        meal_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[FoodLog]:
        statement = (
            select(FoodLog)
            .options(selectinload(FoodLog.items))
            .where(FoodLog.user_id == user_id)
            .order_by(desc(FoodLog.logged_for_date), desc(FoodLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        if logged_for_date is not None:
            statement = statement.where(FoodLog.logged_for_date == logged_for_date)

        if meal_type is not None:
            statement = statement.where(FoodLog.meal_type == meal_type)

        return list(self.db.scalars(statement).all())

    def list_for_user_and_date(
        self,
        user_id: str,
        target_date: date,
    ) -> list[FoodLog]:
        return list(
            self.db.scalars(
                select(FoodLog).where(
                    FoodLog.user_id == user_id,
                    FoodLog.logged_for_date == target_date,
                )
            ).all()
        )