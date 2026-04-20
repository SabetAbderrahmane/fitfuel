from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.source_food_record import SourceFoodRecord


class SourceNutrientRecord(Base, TimestampMixin):
    """
    Raw nutrient row captured from the imported source payload.
    """

    __tablename__ = "source_nutrient_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    source_food_record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_food_records.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    nutrient_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    nutrient_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    payload_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    source_food_record: Mapped["SourceFoodRecord"] = relationship(
        "SourceFoodRecord",
        back_populates="nutrient_records",
    )