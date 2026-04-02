from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserGoal(Base, TimestampMixin):
    """
    Stores user nutrition and body-composition goals over time.

    We keep the computed BMR/TDEE and the formula used so the system can later
    explain exactly how a target was derived.
    """

    __tablename__ = "user_goals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    calculation_mode: Mapped[str] = mapped_column(
        String(20),
        default="calculated",
        nullable=False,
    )
    bmr_formula: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estimated_bmr: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_tdee: Mapped[float | None] = mapped_column(Float, nullable=True)

    target_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    weekly_target_rate_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    target_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    target_protein_g: Mapped[int] = mapped_column(Integer, nullable=False)
    target_carbs_g: Mapped[int] = mapped_column(Integer, nullable=False)
    target_fat_g: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="goals",
    )