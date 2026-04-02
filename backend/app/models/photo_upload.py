from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.photo_prediction import PhotoPrediction
    from app.models.user import User


class PhotoUpload(Base, TimestampMixin):
    """
    Stores uploaded meal/food image metadata.

    This is the ingestion point for the future vision pipeline.
    """

    __tablename__ = "photo_uploads"

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

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    storage_provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="local",
    )
    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    storage_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    local_file_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    upload_status: Mapped[str] = mapped_column(
        String(30),
        default="uploaded",
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[User] = relationship("User")
    predictions: Mapped[list[PhotoPrediction]] = relationship(
        "PhotoPrediction",
        back_populates="photo_upload",
        cascade="all, delete-orphan",
        order_by="desc(PhotoPrediction.created_at)",
    )