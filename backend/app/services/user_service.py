from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_profile import ActivityProfile
from app.models.allergy import Allergy
from app.models.dietary_preference import DietaryPreference
from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ActivityProfileResponse,
    AllergyResponse,
    DietaryPreferenceResponse,
    UserProfileResponse,
    UserProfileUpsertRequest,
)


class UserService:
    """
    Handles user account/profile read and write operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def get_profile(self, current_user: User) -> UserProfile | None:
        return self.db.scalar(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
        )

    def get_activity_profile(self, current_user: User) -> ActivityProfile | None:
        return self.db.scalar(
            select(ActivityProfile).where(ActivityProfile.user_id == current_user.id)
        )

    def list_allergies(self, current_user: User) -> list[Allergy]:
        return list(
            self.db.scalars(
                select(Allergy)
                .where(Allergy.user_id == current_user.id)
                .order_by(Allergy.created_at.desc())
            ).all()
        )

    def list_dietary_preferences(self, current_user: User) -> list[DietaryPreference]:
        return list(
            self.db.scalars(
                select(DietaryPreference)
                .where(DietaryPreference.user_id == current_user.id)
                .order_by(DietaryPreference.created_at.desc())
            ).all()
        )

    def upsert_profile(
        self,
        current_user: User,
        payload: UserProfileUpsertRequest,
    ) -> UserProfileResponse:
        profile = self.get_profile(current_user)

        if profile is None:
            profile = UserProfile(user_id=current_user.id)
            self.db.add(profile)

        profile.first_name = payload.first_name.strip() if payload.first_name else None
        profile.last_name = payload.last_name.strip() if payload.last_name else None
        profile.age = payload.age
        profile.sex = payload.sex.strip() if payload.sex else None
        profile.height_cm = payload.height_cm
        profile.start_weight_kg = payload.start_weight_kg
        profile.current_weight_kg = payload.current_weight_kg

        activity_profile = self.get_activity_profile(current_user)
        if payload.activity_profile is not None:
            if activity_profile is None:
                activity_profile = ActivityProfile(user_id=current_user.id)
                self.db.add(activity_profile)

            activity_profile.activity_level = (
                payload.activity_profile.activity_level.strip()
                if payload.activity_profile.activity_level
                else None
            )
            activity_profile.workout_days_per_week = payload.activity_profile.workout_days_per_week
            activity_profile.preferred_workout_style = (
                payload.activity_profile.preferred_workout_style.strip()
                if payload.activity_profile.preferred_workout_style
                else None
            )
            activity_profile.daily_step_goal = payload.activity_profile.daily_step_goal
            activity_profile.notes = (
                payload.activity_profile.notes.strip()
                if payload.activity_profile.notes
                else None
            )

        existing_allergies = self.list_allergies(current_user)
        for item in existing_allergies:
            self.db.delete(item)

        for item in payload.allergies:
            allergy = Allergy(
                user_id=current_user.id,
                allergen_name=item.allergen_name.strip(),
                severity=item.severity.strip() if item.severity else None,
                notes=item.notes.strip() if item.notes else None,
                is_active=item.is_active,
            )
            self.db.add(allergy)

        existing_preferences = self.list_dietary_preferences(current_user)
        for item in existing_preferences:
            self.db.delete(item)

        for item in payload.dietary_preferences:
            preference = DietaryPreference(
                user_id=current_user.id,
                preference_type=item.preference_type,
                value=item.value.strip(),
                notes=item.notes.strip() if item.notes else None,
                is_active=item.is_active,
            )
            self.db.add(preference)

        self.db.commit()
        self.db.refresh(profile)

        return self.get_full_profile_response(current_user)

    def get_full_profile_response(self, current_user: User) -> UserProfileResponse:
        profile = self.get_profile(current_user)
        if profile is None:
            raise ValueError("Profile not found for this user.")

        activity_profile = self.get_activity_profile(current_user)
        allergies = self.list_allergies(current_user)
        preferences = self.list_dietary_preferences(current_user)

        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            age=profile.age,
            sex=profile.sex,
            height_cm=profile.height_cm,
            start_weight_kg=profile.start_weight_kg,
            current_weight_kg=profile.current_weight_kg,
            activity_profile=(
                ActivityProfileResponse.model_validate(activity_profile)
                if activity_profile is not None
                else None
            ),
            allergies=[AllergyResponse.model_validate(item) for item in allergies],
            dietary_preferences=[
                DietaryPreferenceResponse.model_validate(item) for item in preferences
            ],
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )