from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.grocery_list_item import GroceryListItem
    from app.models.meal_plan import MealPlan
    from app.models.user import User


class GroceryList(Base, TimestampMixin):
    """
    Grocery list generated from a meal plan or created manually later.
    """

    __tablename__ = "grocery_lists"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    meal_plan_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("meal_plans.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    list_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(30),
        default="meal_plan",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    item_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="grocery_lists",
    )
    meal_plan: Mapped[MealPlan | None] = relationship("MealPlan")
    items: Mapped[list[GroceryListItem]] = relationship(
        "GroceryListItem",
        back_populates="grocery_list",
        cascade="all, delete-orphan",
        order_by="GroceryListItem.position.asc()",
    )