from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem
    from app.models.meal_plan import MealPlan


class MealPlanItem(Base, TimestampMixin):
    """
    A single planned food inside a daily meal plan.
    """

    __tablename__ = "meal_plan_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    meal_plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    source_recipe_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("recipes.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_template_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("meal_templates.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_recipe_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    source_template_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    source_generation_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    meal_slot: Mapped[str] = mapped_column(
        String(30),
        index=True,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        default=1,
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

    planned_quantity: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    planned_grams: Mapped[float] = mapped_column(
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

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    meal_plan: Mapped[MealPlan] = relationship(
        "MealPlan",
        back_populates="items",
    )
    food_item: Mapped[FoodItem] = relationship("FoodItem")
