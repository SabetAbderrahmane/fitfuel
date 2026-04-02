from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class DietaryPreference(Base, TimestampMixin):
    """
    Normalized dietary preference entry for a user.

    Examples:
    - preference_type = "diet_type", value = "vegetarian"
    - preference_type = "disliked_food", value = "broccoli"
    - preference_type = "preferred_food", value = "salmon"
    - preference_type = "restriction", value = "halal"
    """

    __tablename__ = "dietary_preferences"

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

    preference_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="dietary_preferences",
    )