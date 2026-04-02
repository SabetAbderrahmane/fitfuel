from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem
    from app.models.food_log import FoodLog


class FoodLogItem(Base, TimestampMixin):
    """
    A single food entry inside a meal log.

    Nutrient values are snapshotted at log time so history stays stable
    even if the food catalog changes later.
    """

    __tablename__ = "food_log_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    food_log_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_logs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    food_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    brand_snapshot: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    grams: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    calories: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    protein_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    carbs_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    fat_g: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    food_log: Mapped[FoodLog] = relationship(
        "FoodLog",
        back_populates="items",
    )
    food_item: Mapped[FoodItem] = relationship("FoodItem")