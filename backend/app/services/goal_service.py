from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.ai.nutrition.bmr import BMRInput, calculate_bmr
from app.ai.nutrition.macro_calculator import calculate_macros
from app.ai.nutrition.tdee import calculate_goal_calories, calculate_tdee
from app.models.activity_profile import ActivityProfile
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.goal import UserGoalCreateRequest


class GoalService:
    """
    Handles nutrition and body-composition goal management.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _deactivate_existing_goals(self, user_id: str) -> None:
        active_goals = self.db.scalars(
            select(UserGoal).where(
                UserGoal.user_id == user_id,
                UserGoal.is_active.is_(True),
            )
        ).all()

        for goal in active_goals:
            goal.is_active = False
            goal.ended_at = datetime.now(timezone.utc)

    def _get_required_profile_for_calculation(
        self,
        user_id: str,
    ) -> tuple[UserProfile, ActivityProfile]:
        profile = self.db.scalar(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        activity_profile = self.db.scalar(
            select(ActivityProfile).where(ActivityProfile.user_id == user_id)
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile is required before creating a calculated goal.",
            )

        if activity_profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Activity profile is required before creating a calculated goal.",
            )

        missing_fields: list[str] = []

        if profile.age is None:
            missing_fields.append("age")
        if profile.sex is None:
            missing_fields.append("sex")
        if profile.height_cm is None:
            missing_fields.append("height_cm")
        if profile.current_weight_kg is None:
            missing_fields.append("current_weight_kg")
        if activity_profile.activity_level is None:
            missing_fields.append("activity_profile.activity_level")

        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Profile is incomplete for nutrition calculation. "
                    f"Missing fields: {', '.join(missing_fields)}."
                ),
            )

        return profile, activity_profile

    def _build_calculated_goal(self, current_user: User, payload: UserGoalCreateRequest) -> UserGoal:
        profile, activity_profile = self._get_required_profile_for_calculation(current_user.id)

        bmr_input = BMRInput(
            age=profile.age,  # type: ignore[arg-type]
            sex=profile.sex,  # type: ignore[arg-type]
            height_cm=profile.height_cm,  # type: ignore[arg-type]
            weight_kg=profile.current_weight_kg,  # type: ignore[arg-type]
        )

        try:
            estimated_bmr = calculate_bmr(
                bmr_input,
                formula=payload.bmr_formula,
            )
            estimated_tdee = calculate_tdee(
                estimated_bmr,
                activity_profile.activity_level,  # type: ignore[arg-type]
            )
            target_calories = calculate_goal_calories(
                estimated_tdee,
                goal_type=payload.goal_type,
                weekly_target_rate_kg=payload.weekly_target_rate_kg,
            )
            macros = calculate_macros(
                target_calories=target_calories,
                weight_kg=profile.current_weight_kg,  # type: ignore[arg-type]
                goal_type=payload.goal_type,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        return UserGoal(
            user_id=current_user.id,
            goal_type=payload.goal_type,
            notes=payload.notes,
            calculation_mode=payload.calculation_mode,
            bmr_formula=payload.bmr_formula,
            estimated_bmr=estimated_bmr,
            estimated_tdee=estimated_tdee,
            target_weight_kg=payload.target_weight_kg,
            weekly_target_rate_kg=payload.weekly_target_rate_kg,
            target_calories=macros.calories,
            target_protein_g=macros.protein_g,
            target_carbs_g=macros.carbs_g,
            target_fat_g=macros.fat_g,
            is_active=True,
        )

    def _build_manual_goal(self, current_user: User, payload: UserGoalCreateRequest) -> UserGoal:
        required_manual_fields = {
            "target_calories": payload.target_calories,
            "target_protein_g": payload.target_protein_g,
            "target_carbs_g": payload.target_carbs_g,
            "target_fat_g": payload.target_fat_g,
        }

        missing = [field for field, value in required_manual_fields.items() if value is None]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Manual goal mode requires these fields: "
                    + ", ".join(missing)
                    + "."
                ),
            )

        return UserGoal(
            user_id=current_user.id,
            goal_type=payload.goal_type,
            notes=payload.notes,
            calculation_mode=payload.calculation_mode,
            bmr_formula=None,
            estimated_bmr=None,
            estimated_tdee=None,
            target_weight_kg=payload.target_weight_kg,
            weekly_target_rate_kg=payload.weekly_target_rate_kg,
            target_calories=payload.target_calories,  # type: ignore[arg-type]
            target_protein_g=payload.target_protein_g,  # type: ignore[arg-type]
            target_carbs_g=payload.target_carbs_g,  # type: ignore[arg-type]
            target_fat_g=payload.target_fat_g,  # type: ignore[arg-type]
            is_active=True,
        )

    def create_goal(
        self,
        current_user: User,
        payload: UserGoalCreateRequest,
    ) -> UserGoal:
        self._deactivate_existing_goals(current_user.id)

        if payload.calculation_mode == "calculated":
            new_goal = self._build_calculated_goal(current_user, payload)
        else:
            new_goal = self._build_manual_goal(current_user, payload)

        self.db.add(new_goal)
        self.db.commit()
        self.db.refresh(new_goal)

        return new_goal

    def list_goals(self, current_user: User) -> list[UserGoal]:
        return list(
            self.db.scalars(
                select(UserGoal)
                .where(UserGoal.user_id == current_user.id)
                .order_by(desc(UserGoal.started_at))
            ).all()
        )

    def get_current_goal(self, current_user: User) -> UserGoal:
        goal = self.db.scalar(
            select(UserGoal)
            .where(
                UserGoal.user_id == current_user.id,
                UserGoal.is_active.is_(True),
            )
            .order_by(desc(UserGoal.started_at))
        )

        if goal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active goal found for this user.",
            )

        return goal