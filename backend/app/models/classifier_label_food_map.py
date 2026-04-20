from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.classifier_label import ClassifierLabel
    from app.models.food_item import FoodItem


class ClassifierLabelFoodMap(Base, TimestampMixin):
    """
    Explicit bridge from an AI classifier label to a normalized food item.
    """

    __tablename__ = "classifier_label_food_maps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    classifier_label_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("classifier_labels.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    map_type: Mapped[str] = mapped_column(
        String(30),
        default="exact",
        nullable=False,
    )
    ranking: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    match_confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    requires_user_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    classifier_label: Mapped["ClassifierLabel"] = relationship(
        "ClassifierLabel",
        back_populates="food_maps",
    )
    food_item: Mapped["FoodItem"] = relationship(
        "FoodItem",
        back_populates="classifier_label_food_maps",
    )