from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.activity_log import ActivityLog
    from app.models.activity_profile import ActivityProfile
    from app.models.allergy import Allergy
    from app.models.audit_log import AuditLog
    from app.models.chat_session import ChatSession
    from app.models.dietary_preference import DietaryPreference
    from app.models.food_log import FoodLog
    from app.models.grocery_list import GroceryList
    from app.models.meal_plan import MealPlan
    from app.models.photo_upload import PhotoUpload
    from app.models.progress_snapshot import ProgressSnapshot
    from app.models.recipe import Recipe
    from app.models.refresh_token import RefreshToken
    from app.models.user_goal import UserGoal
    from app.models.user_profile import UserProfile
    from app.models.weight_log import WeightLog


class User(Base, TimestampMixin):
    """
    Core authentication identity.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile: Mapped[UserProfile | None] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    activity_profile: Mapped[ActivityProfile | None] = relationship(
        "ActivityProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    allergies: Mapped[list[Allergy]] = relationship(
        "Allergy",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Allergy.created_at.desc()",
    )
    dietary_preferences: Mapped[list[DietaryPreference]] = relationship(
        "DietaryPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="DietaryPreference.created_at.desc()",
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ActivityLog.logged_for_date.desc()",
    )

    goals: Mapped[list[UserGoal]] = relationship(
        "UserGoal",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(UserGoal.started_at)",
    )
    food_logs: Mapped[list[FoodLog]] = relationship(
        "FoodLog",
        cascade="all, delete-orphan",
    )
    weight_logs: Mapped[list[WeightLog]] = relationship(
        "WeightLog",
        cascade="all, delete-orphan",
    )
    progress_snapshots: Mapped[list[ProgressSnapshot]] = relationship(
        "ProgressSnapshot",
        cascade="all, delete-orphan",
    )
    meal_plans: Mapped[list[MealPlan]] = relationship(
        "MealPlan",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(MealPlan.plan_date)",
    )
    photo_uploads: Mapped[list[PhotoUpload]] = relationship(
        "PhotoUpload",
        cascade="all, delete-orphan",
        order_by="desc(PhotoUpload.created_at)",
    )
    created_recipes: Mapped[list[Recipe]] = relationship(
        "Recipe",
        back_populates="created_by_user",
        order_by="desc(Recipe.created_at)",
    )
    grocery_lists: Mapped[list[GroceryList]] = relationship(
        "GroceryList",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(GroceryList.list_date)",
    )
    chat_sessions: Mapped[list[ChatSession]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(ChatSession.updated_at)",
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(RefreshToken.created_at)",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog",
        back_populates="user",
        order_by="desc(AuditLog.created_at)",
    )