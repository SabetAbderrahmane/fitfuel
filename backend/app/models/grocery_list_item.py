from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem
    from app.models.grocery_list import GroceryList


class GroceryListItem(Base, TimestampMixin):
    """
    Aggregated grocery list item.

    The item can point to a food catalog record when known, while also storing
    a stable snapshot name/category for display.
    """

    __tablename__ = "grocery_list_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    grocery_list_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("grocery_lists.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    food_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    item_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    category_snapshot: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    total_grams: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    quantity_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_checked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    grocery_list: Mapped[GroceryList] = relationship(
        "GroceryList",
        back_populates="items",
    )
    food_item: Mapped[FoodItem | None] = relationship("FoodItem")