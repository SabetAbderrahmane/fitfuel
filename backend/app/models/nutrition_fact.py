from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem


class NutritionFact(Base, TimestampMixin):
    """
    Nutrition values normalized per 100 grams.

    This keeps calorie estimation and portion scaling straightforward:
    final_value = (grams / 100) * nutrient_per_100g
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

    food_item: Mapped[FoodItem] = relationship(
        "FoodItem",
        back_populates="nutrition_fact",
    )