from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ActivityLog(Base, TimestampMixin):
    """
    Stores workout or physical activity events for a user.
    """

    __tablename__ = "activity_logs"

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
    activity_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    calories_burned: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    intensity: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="activity_logs",
    )