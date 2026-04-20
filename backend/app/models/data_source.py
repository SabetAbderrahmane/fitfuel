from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food_source_link import FoodSourceLink
    from app.models.ingestion_release import IngestionRelease


class DataSource(Base, TimestampMixin):
    """
    Registry of external or model-side source systems.
    """

    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    source_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    license_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    homepage_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    ingestion_releases: Mapped[list["IngestionRelease"]] = relationship(
        "IngestionRelease",
        back_populates="data_source",
        cascade="all, delete-orphan",
        order_by="desc(IngestionRelease.created_at)",
    )
    food_source_links: Mapped[list["FoodSourceLink"]] = relationship(
        "FoodSourceLink",
        back_populates="data_source",
        cascade="all, delete-orphan",
    )