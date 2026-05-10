from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CheckConstraint, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ai_feedback_history import AIFeedbackHistory
    from app.models.classifier_label import ClassifierLabel
    from app.models.food_item import FoodItem
    from app.models.photo_prediction_candidate import PhotoPredictionCandidate
    from app.models.photo_upload import PhotoUpload


class PhotoPrediction(Base, TimestampMixin):
    """
    Stores model or manually attached prediction results for an uploaded image.
    """

    __tablename__ = "photo_predictions"
    __table_args__ = (
        CheckConstraint(
            "prediction_status IN "
            "('pending', 'completed', 'failed', 'confirmed', 'corrected', 'rejected')",
            name="prediction_status_valid",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    photo_upload_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("photo_uploads.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    predicted_food_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    selected_classifier_label_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("classifier_labels.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        default="manual_placeholder",
        nullable=False,
    )
    prediction_status: Mapped[str] = mapped_column(
        String(30),
        default="completed",
        nullable=False,
    )
    predicted_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    estimated_grams: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_calories: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_protein_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_carbs_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_fat_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    inference_metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    photo_upload: Mapped["PhotoUpload"] = relationship(
        "PhotoUpload",
        back_populates="predictions",
    )
    predicted_food_item: Mapped["FoodItem | None"] = relationship("FoodItem")
    selected_classifier_label: Mapped["ClassifierLabel | None"] = relationship(
        "ClassifierLabel",
        back_populates="selected_predictions",
    )
    candidates: Mapped[list["PhotoPredictionCandidate"]] = relationship(
        "PhotoPredictionCandidate",
        back_populates="photo_prediction",
        cascade="all, delete-orphan",
        order_by="PhotoPredictionCandidate.candidate_rank.asc()",
    )
    feedback_entries: Mapped[list["AIFeedbackHistory"]] = relationship(
        "AIFeedbackHistory",
        back_populates="photo_prediction",
        cascade="all, delete-orphan",
        order_by="desc(AIFeedbackHistory.created_at)",
    )
