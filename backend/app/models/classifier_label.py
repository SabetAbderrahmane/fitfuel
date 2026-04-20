from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.classifier_label_food_map import ClassifierLabelFoodMap
    from app.models.photo_prediction import PhotoPrediction
    from app.models.photo_prediction_candidate import PhotoPredictionCandidate


class ClassifierLabel(Base, TimestampMixin):
    """
    Versionable classifier vocabulary row.

    This is intentionally simpler than the full label_set model from the
    remodelling report so it fits the repo's current flat model layout.
    """

    __tablename__ = "classifier_labels"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    label_set_name: Mapped[str] = mapped_column(
        String(100),
        default="food101",
        nullable=False,
    )
    raw_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    normalized_label: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    display_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    food_maps: Mapped[list["ClassifierLabelFoodMap"]] = relationship(
        "ClassifierLabelFoodMap",
        back_populates="classifier_label",
        cascade="all, delete-orphan",
        order_by="ClassifierLabelFoodMap.ranking.asc()",
    )
    selected_predictions: Mapped[list["PhotoPrediction"]] = relationship(
        "PhotoPrediction",
        back_populates="selected_classifier_label",
    )
    prediction_candidates: Mapped[list["PhotoPredictionCandidate"]] = relationship(
        "PhotoPredictionCandidate",
        back_populates="classifier_label",
    )