from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class FailedLoginAttempt(Base, TimestampMixin):
    """
    Stores failed authentication attempts for basic monitoring and later lockout logic.
    """

    __tablename__ = "failed_login_attempts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    failure_reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )