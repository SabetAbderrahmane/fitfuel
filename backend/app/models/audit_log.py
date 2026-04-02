from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base, TimestampMixin):
    """
    Stores important security and operational events.
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    entity_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    details_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[User | None] = relationship(
        "User",
        back_populates="audit_logs",
    )