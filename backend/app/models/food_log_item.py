from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem
    from app.models.food_log import FoodLog
    from app.models.photo_prediction import PhotoPrediction


class FoodLogItem(Base, TimestampMixin):
    """
    A single food entry inside a meal log.
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
    photo_prediction_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("photo_predictions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    food_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    brand_snapshot: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    serving_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source_snapshot: Mapped[dict | None] = mapped_column(
        JSON,
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

    food_log: Mapped["FoodLog"] = relationship(
        "FoodLog",
        back_populates="items",
    )
    food_item: Mapped["FoodItem"] = relationship("FoodItem")
    photo_prediction: Mapped["PhotoPrediction | None"] = relationship(
        "PhotoPrediction",
    )