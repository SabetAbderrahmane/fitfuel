from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.food_log import FoodLog
from app.models.progress_snapshot import ProgressSnapshot
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.weight_log import WeightLog
from app.repositories.food_log_repository import FoodLogRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.progress import WeightLogCreateRequest


class ProgressService:
    """
    Handles weight tracking and daily adherence snapshot generation.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.food_log_repository = FoodLogRepository(db)
        self.goal_repository = GoalRepository(db)
        self.progress_repository = ProgressRepository(db)

    def create_weight_log(
        self,
        current_user: User,
        payload: WeightLogCreateRequest,
    ) -> WeightLog:
        weight_log = WeightLog(
            user_id=current_user.id,
            logged_for_date=payload.logged_for_date,
            weight_kg=round(payload.weight_kg, 2),
            notes=payload.notes.strip() if payload.notes else None,
        )

        self.db.add(weight_log)
        self.db.commit()
        self.db.refresh(weight_log)

        return weight_log

    def list_weight_logs(
        self,
        current_user: User,
        limit: int = 30,
        offset: int = 0,
    ) -> list[WeightLog]:
        return self.progress_repository.list_weight_logs_for_user(
            current_user.id,
            limit=limit,
            offset=offset,
        )

    def _get_active_goal(self, user_id: str) -> UserGoal:
        goal = self.goal_repository.get_active_for_user(user_id)

        if goal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active goal found for this user.",
            )

        return goal

    def _get_latest_weight_on_or_before(
        self,
        user_id: str,
        target_date: date,
    ) -> WeightLog | None:
        return self.progress_repository.get_latest_weight_on_or_before(user_id, target_date)

    def _get_food_logs_for_date(
        self,
        user_id: str,
        target_date: date,
    ) -> list[FoodLog]:
        return self.food_log_repository.list_for_user_and_date(user_id, target_date)

    @staticmethod
    def _adherence_percent(consumed: float, target: float) -> float:
        if target <= 0:
            return 0.0

        difference_ratio = abs(consumed - target) / target
        score = max(0.0, 100.0 - (difference_ratio * 100.0))
        return round(score, 2)

    @staticmethod
    def _overall_score(
        calorie_pct: float,
        protein_pct: float,
        carbs_pct: float,
        fat_pct: float,
    ) -> float:
        score = (
            (0.40 * calorie_pct)
            + (0.30 * protein_pct)
            + (0.15 * carbs_pct)
            + (0.15 * fat_pct)
        )
        return round(score, 2)

    def generate_daily_snapshot(
        self,
        current_user: User,
        snapshot_date: date,
    ) -> ProgressSnapshot:
        active_goal = self._get_active_goal(current_user.id)
        latest_weight = self._get_latest_weight_on_or_before(current_user.id, snapshot_date)
        food_logs = self._get_food_logs_for_date(current_user.id, snapshot_date)

        consumed_calories = round(sum(log.total_calories for log in food_logs), 2)
        consumed_protein_g = round(sum(log.total_protein_g for log in food_logs), 2)
        consumed_carbs_g = round(sum(log.total_carbs_g for log in food_logs), 2)
        consumed_fat_g = round(sum(log.total_fat_g for log in food_logs), 2)

        calorie_adherence_pct = self._adherence_percent(
            consumed_calories,
            float(active_goal.target_calories),
        )
        protein_adherence_pct = self._adherence_percent(
            consumed_protein_g,
            float(active_goal.target_protein_g),
        )
        carbs_adherence_pct = self._adherence_percent(
            consumed_carbs_g,
            float(active_goal.target_carbs_g),
        )
        fat_adherence_pct = self._adherence_percent(
            consumed_fat_g,
            float(active_goal.target_fat_g),
        )

        overall_adherence_score = self._overall_score(
            calorie_pct=calorie_adherence_pct,
            protein_pct=protein_adherence_pct,
            carbs_pct=carbs_adherence_pct,
            fat_pct=fat_adherence_pct,
        )

        existing_snapshot = self.progress_repository.get_snapshot_for_user_and_date(
            current_user.id,
            snapshot_date,
        )

        snapshot = existing_snapshot or ProgressSnapshot(
            user_id=current_user.id,
            snapshot_date=snapshot_date,
            target_calories=active_goal.target_calories,
            target_protein_g=active_goal.target_protein_g,
            target_carbs_g=active_goal.target_carbs_g,
            target_fat_g=active_goal.target_fat_g,
        )

        snapshot.current_weight_kg = latest_weight.weight_kg if latest_weight else None
        snapshot.target_weight_kg = active_goal.target_weight_kg

        snapshot.consumed_calories = consumed_calories
        snapshot.consumed_protein_g = consumed_protein_g
        snapshot.consumed_carbs_g = consumed_carbs_g
        snapshot.consumed_fat_g = consumed_fat_g

        snapshot.target_calories = active_goal.target_calories
        snapshot.target_protein_g = active_goal.target_protein_g
        snapshot.target_carbs_g = active_goal.target_carbs_g
        snapshot.target_fat_g = active_goal.target_fat_g

        snapshot.calorie_adherence_pct = calorie_adherence_pct
        snapshot.protein_adherence_pct = protein_adherence_pct
        snapshot.carbs_adherence_pct = carbs_adherence_pct
        snapshot.fat_adherence_pct = fat_adherence_pct
        snapshot.overall_adherence_score = overall_adherence_score

        if existing_snapshot is None:
            self.db.add(snapshot)

        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def list_progress_snapshots(
        self,
        current_user: User,
        limit: int = 30,
        offset: int = 0,
    ) -> list[ProgressSnapshot]:
        return self.progress_repository.list_snapshots_for_user(
            current_user.id,
            limit=limit,
            offset=offset,
        )

    def get_progress_snapshot(
        self,
        current_user: User,
        snapshot_id: str,
    ) -> ProgressSnapshot:
        snapshot = self.progress_repository.get_snapshot_for_user(
            current_user.id,
            snapshot_id,
        )

        if snapshot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress snapshot not found.",
            )

        return snapshot