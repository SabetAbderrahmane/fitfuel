from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ProgressSnapshot(Base, TimestampMixin):
    """
    Stores daily computed progress data for dashboard rendering and weekly summaries.
    """

    __tablename__ = "progress_snapshots"

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

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )

    current_weight_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    target_weight_kg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    consumed_calories: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    consumed_protein_g: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    consumed_carbs_g: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    consumed_fat_g: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    target_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    target_protein_g: Mapped[int] = mapped_column(Integer, nullable=False)
    target_carbs_g: Mapped[int] = mapped_column(Integer, nullable=False)
    target_fat_g: Mapped[int] = mapped_column(Integer, nullable=False)

    calorie_adherence_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    protein_adherence_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    carbs_adherence_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    fat_adherence_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    overall_adherence_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    user: Mapped[User] = relationship("User")