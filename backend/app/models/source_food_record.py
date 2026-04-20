from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ingestion_release import IngestionRelease
    from app.models.source_nutrient_record import SourceNutrientRecord


class SourceFoodRecord(Base, TimestampMixin):
    """
    Raw source-side food record retained for provenance and repeatable imports.
    """

    __tablename__ = "source_food_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    ingestion_release_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ingestion_releases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_record_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    source_food_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    brand_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    payload_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    normalized_hash: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )

    ingestion_release: Mapped["IngestionRelease"] = relationship(
        "IngestionRelease",
        back_populates="source_food_records",
    )
    nutrient_records: Mapped[list["SourceNutrientRecord"]] = relationship(
        "SourceNutrientRecord",
        back_populates="source_food_record",
        cascade="all, delete-orphan",
        order_by="SourceNutrientRecord.created_at.asc()",
    )