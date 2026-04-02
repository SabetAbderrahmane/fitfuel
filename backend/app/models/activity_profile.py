from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ActivityProfile(Base, TimestampMixin):
    """
    One-to-one user activity profile used for TDEE calculation and future workout logic.
    """

    __tablename__ = "activity_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    activity_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    workout_days_per_week: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    preferred_workout_style: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    daily_step_goal: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="activity_profile",
    )