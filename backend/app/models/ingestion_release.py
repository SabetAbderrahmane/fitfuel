from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.data_source import DataSource
    from app.models.food_source_link import FoodSourceLink
    from app.models.source_food_record import SourceFoodRecord


class IngestionRelease(Base, TimestampMixin):
    """
    Immutable-ish release/version metadata for one source import batch.
    """

    __tablename__ = "ingestion_releases"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    data_source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    checksum_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="draft",
        nullable=False,
    )
    raw_record_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    normalized_record_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    data_source: Mapped["DataSource"] = relationship(
        "DataSource",
        back_populates="ingestion_releases",
    )
    source_food_records: Mapped[list["SourceFoodRecord"]] = relationship(
        "SourceFoodRecord",
        back_populates="ingestion_release",
        cascade="all, delete-orphan",
    )
    food_source_links: Mapped[list["FoodSourceLink"]] = relationship(
        "FoodSourceLink",
        back_populates="ingestion_release",
        cascade="all, delete-orphan",
    )