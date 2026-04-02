from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user import UserProfileResponse, UserProfileUpsertRequest


class UserService:
    """
    Handles user account/profile read and write operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _join_csv(items: list[str]) -> str | None:
        cleaned = [item.strip() for item in items if item.strip()]
        return ", ".join(cleaned) if cleaned else None

    @staticmethod
    def _split_csv(value: str | None) -> list[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    def get_profile(self, current_user: User) -> UserProfile | None:
        return self.db.scalar(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
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

        profile.first_name = payload.first_name
        profile.last_name = payload.last_name
        profile.age = payload.age
        profile.sex = payload.sex
        profile.height_cm = payload.height_cm
        profile.start_weight_kg = payload.start_weight_kg
        profile.current_weight_kg = payload.current_weight_kg
        profile.activity_level = payload.activity_level
        profile.diet_type = payload.diet_type
        profile.allergies_csv = self._join_csv(payload.allergies)
        profile.disliked_foods_csv = self._join_csv(payload.disliked_foods)

        self.db.commit()
        self.db.refresh(profile)

        return self.to_profile_response(profile)

    def to_profile_response(self, profile: UserProfile) -> UserProfileResponse:
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
            activity_level=profile.activity_level,
            diet_type=profile.diet_type,
            allergies=self._split_csv(profile.allergies_csv),
            disliked_foods=self._split_csv(profile.disliked_foods_csv),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )