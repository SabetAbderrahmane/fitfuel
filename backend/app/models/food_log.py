from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_log_item import FoodLogItem
    from app.models.user import User


class FoodLog(Base, TimestampMixin):
    """
    A single meal log for a user on a specific date.

    Example:
    - breakfast on 2026-04-02
    - lunch on 2026-04-02
    """

    __tablename__ = "food_logs"

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

    logged_for_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )
    meal_type: Mapped[str] = mapped_column(
        String(30),
        index=True,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    total_calories: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_protein_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_carbs_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_fat_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    user: Mapped[User] = relationship("User")
    items: Mapped[list[FoodLogItem]] = relationship(
        "FoodLogItem",
        back_populates="food_log",
        cascade="all, delete-orphan",
    )