from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base, TimestampMixin):
    """
    Stores core onboarding and body/profile information.

    Dynamic lifestyle preferences are normalized into separate tables:
    - activity_profiles
    - allergies
    - dietary_preferences
    """

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(20), nullable=True)

    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    user: Mapped[User] = relationship(
        "User",
        back_populates="profile",
    )