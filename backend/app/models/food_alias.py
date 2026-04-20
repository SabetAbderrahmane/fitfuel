from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_item import FoodItem


class FoodAlias(Base, TimestampMixin):
    """
    Exact/synonym/fuzzy alias rows for the normalized food catalog.
    """

    __tablename__ = "food_aliases"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    alias_text: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    normalized_alias: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    alias_type: Mapped[str] = mapped_column(
        String(30),
        default="synonym",
        nullable=False,
    )
    language_code: Mapped[str | None] = mapped_column(
        String(10),
        default="en",
        nullable=True,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    food_item: Mapped["FoodItem"] = relationship(
        "FoodItem",
        back_populates="aliases",
    )