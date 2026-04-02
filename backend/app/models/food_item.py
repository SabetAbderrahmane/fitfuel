from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.nutrition_fact import NutritionFact


class FoodItem(Base, TimestampMixin):
    """
    Food catalog entry.

    This is the canonical food identity used by manual logging, meal planning,
    AI nutrition matching, and later photo-based estimation.
    """

    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    brand: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    default_serving_size_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    default_serving_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        default="manual",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    nutrition_fact: Mapped[NutritionFact | None] = relationship(
        "NutritionFact",
        back_populates="food_item",
        uselist=False,
        cascade="all, delete-orphan",
    )