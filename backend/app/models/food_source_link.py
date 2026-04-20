from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.data_source import DataSource
    from app.models.ingestion_release import IngestionRelease


class FoodSourceLink(Base, TimestampMixin):
    """
    Provenance bridge between one normalized food item and one source-side record.
    """

    __tablename__ = "food_source_links"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    food_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("food_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    data_source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
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
    source_priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    data_source: Mapped["DataSource"] = relationship(
        "DataSource",
        back_populates="food_source_links",
    )
    ingestion_release: Mapped["IngestionRelease"] = relationship(
        "IngestionRelease",
        back_populates="food_source_links",
    )