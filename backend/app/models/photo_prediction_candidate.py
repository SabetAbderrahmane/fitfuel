from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.classifier_label import ClassifierLabel
    from app.models.food_item import FoodItem
    from app.models.photo_prediction import PhotoPrediction


class PhotoPredictionCandidate(Base, TimestampMixin):
    """
    Ranked candidate rows produced by inference + catalog mapping.
    """

    __tablename__ = "photo_prediction_candidates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    photo_prediction_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("photo_predictions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    candidate_rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    classifier_label_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("classifier_labels.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    food_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    vision_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    mapping_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    combined_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    explanation_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    photo_prediction: Mapped["PhotoPrediction"] = relationship(
        "PhotoPrediction",
        back_populates="candidates",
    )
    classifier_label: Mapped["ClassifierLabel | None"] = relationship(
        "ClassifierLabel",
        back_populates="prediction_candidates",
    )
    food_item: Mapped["FoodItem | None"] = relationship(
        "FoodItem",
        back_populates="prediction_candidates",
    )