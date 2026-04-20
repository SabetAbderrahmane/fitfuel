from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem


class NutritionFact(Base, TimestampMixin):
    """
    Nutrition values normalized per 100 grams.

    Core macros remain typed columns for efficient dashboard aggregation and
    photo-estimation math. Long-tail micronutrients live in JSON.
    """

    __tablename__ = "nutrition_facts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)

    fiber_g_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)

    micronutrients_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    source_quality: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    food_item: Mapped["FoodItem"] = relationship(
        "FoodItem",
        back_populates="nutrition_fact",
    )