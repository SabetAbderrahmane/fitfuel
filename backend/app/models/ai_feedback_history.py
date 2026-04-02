from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.photo_prediction import PhotoPrediction
    from app.models.photo_upload import PhotoUpload
    from app.models.user import User


class AIFeedbackHistory(Base, TimestampMixin):
    """
    Stores user review actions for AI-generated predictions.

    This becomes useful later for:
    - auditability
    - training data improvement
    - understanding model failure patterns
    """

    __tablename__ = "ai_feedback_history"

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
    photo_upload_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("photo_uploads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    photo_prediction_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("photo_predictions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    feedback_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    original_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    corrected_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_food_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    corrected_food_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="SET NULL"),
        nullable=True,
    )

    original_estimated_grams: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    corrected_estimated_grams: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    original_estimated_calories: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    corrected_estimated_calories: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[User] = relationship("User")
    photo_upload: Mapped[PhotoUpload] = relationship("PhotoUpload")
    photo_prediction: Mapped[PhotoPrediction] = relationship(
        "PhotoPrediction",
        back_populates="feedback_entries",
    )