from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.user import User


class MealTemplate(Base, TimestampMixin):
    """
    Reusable meal template.

    A template can be:
    - linked to a recipe
    - manually defined with estimated macros
    - later used by the frontend when building quick meal plans
    """

    __tablename__ = "meal_templates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    recipe_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("recipes.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
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
    meal_slot: Mapped[str | None] = mapped_column(
        String(30),
        index=True,
        nullable=True,
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    diet_type: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
        nullable=True,
    )
    diet_tags_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    allergen_flags_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        default="manual",
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_calories: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_protein_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_carbs_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_fat_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_by_user: Mapped[User | None] = relationship(
        "User",
        back_populates="meal_templates",
    )
    recipe: Mapped[Recipe | None] = relationship("Recipe")
