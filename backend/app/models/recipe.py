from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.recipe_ingredient import RecipeIngredient
    from app.models.user import User


class Recipe(Base, TimestampMixin):
    """
    Recipe catalog entry with ingredient snapshots and rolled-up nutrition totals.
    """

    __tablename__ = "recipes"

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
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    prep_time_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    cook_time_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    servings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
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

    total_calories: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_protein_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_carbs_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )
    total_fat_g: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    created_by_user: Mapped[User | None] = relationship(
        "User",
        back_populates="created_recipes",
    )
    ingredients: Mapped[list[RecipeIngredient]] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.position.asc()",
    )