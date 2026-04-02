from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.meal_plan import MealPlan
from app.repositories.base import BaseRepository


class MealPlanRepository(BaseRepository[MealPlan]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, MealPlan)

    def get_for_user(self, user_id: str, meal_plan_id: str) -> MealPlan | None:
        return self.db.scalar(
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == user_id,
            )
        )

    def list_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MealPlan]:
        statement = (
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(MealPlan.user_id == user_id)
            .order_by(desc(MealPlan.plan_date), desc(MealPlan.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_latest_for_user(self, user_id: str) -> MealPlan | None:
        return self.db.scalar(
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(MealPlan.user_id == user_id)
            .order_by(desc(MealPlan.plan_date), desc(MealPlan.created_at))
        )