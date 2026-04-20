from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.classifier_label_food_map import ClassifierLabelFoodMap
    from app.models.food_alias import FoodAlias
    from app.models.nutrition_fact import NutritionFact
    from app.models.photo_prediction_candidate import PhotoPredictionCandidate


class FoodItem(Base, TimestampMixin):
    """
    Food catalog entry.

    This remains compatible with the repo's current model shape while adding
    the minimum catalog/search fields required by the database remodelling
    addendum.
    """

    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    brand: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    category: Mapped[str | None] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    default_serving_size_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    default_serving_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        default="manual",
        nullable=False,
    )

    normalized_name: Mapped[str] = mapped_column(
        String(255),
        default="",
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        default="",
        index=True,
        nullable=False,
    )
    search_name: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=False,
    )
    search_tsv: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )

    usage_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    popularity_score: Mapped[float] = mapped_column(
        Numeric(10, 4, asdecimal=False),
        default=0,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    nutrition_fact: Mapped["NutritionFact | None"] = relationship(
        "NutritionFact",
        back_populates="food_item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    aliases: Mapped[list["FoodAlias"]] = relationship(
        "FoodAlias",
        back_populates="food_item",
        cascade="all, delete-orphan",
        order_by="FoodAlias.normalized_alias.asc()",
    )
    classifier_label_food_maps: Mapped[list["ClassifierLabelFoodMap"]] = relationship(
        "ClassifierLabelFoodMap",
        back_populates="food_item",
        cascade="all, delete-orphan",
        order_by="ClassifierLabelFoodMap.ranking.asc()",
    )
    prediction_candidates: Mapped[list["PhotoPredictionCandidate"]] = relationship(
        "PhotoPredictionCandidate",
        back_populates="food_item",
    )