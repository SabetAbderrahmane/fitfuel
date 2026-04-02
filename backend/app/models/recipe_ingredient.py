from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem
    from app.models.recipe import Recipe


class RecipeIngredient(Base, TimestampMixin):
    """
    Ingredient snapshot inside a recipe.

    We store the food reference plus a snapshot label and grams so recipe history
    remains stable even if the food catalog changes later.
    """

    __tablename__ = "recipe_ingredients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    recipe_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    ingredient_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    quantity_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    grams: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recipe: Mapped[Recipe] = relationship(
        "Recipe",
        back_populates="ingredients",
    )
    food_item: Mapped[FoodItem] = relationship("FoodItem")