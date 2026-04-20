from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.data_ingestion.normalization import upsert_food_alias
from app.db.session import SessionLocal
from app.models.food_item import FoodItem
from app.models.food_source_link import FoodSourceLink
from app.models.ingestion_release import IngestionRelease
from app.models.source_food_record import SourceFoodRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or backfill aliases for existing food_items."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Optional food_items.source filter, e.g. 'usda_fdc' or 'manual'.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional row limit for incremental runs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        statement = select(FoodItem).order_by(FoodItem.created_at.desc())
        if args.source:
            statement = statement.where(FoodItem.source == args.source)
        if args.limit:
            statement = statement.limit(args.limit)

        food_items = list(db.scalars(statement).all())
        alias_count = 0

        for food_item in food_items:
            if food_item.name:
                if upsert_food_alias(
                    db,
                    food_item_id=food_item.id,
                    alias_text=food_item.name,
                    alias_type="exact",
                    confidence_score=1.0,
                ):
                    alias_count += 1

            if food_item.display_name and food_item.display_name != food_item.name:
                if upsert_food_alias(
                    db,
                    food_item_id=food_item.id,
                    alias_text=food_item.display_name,
                    alias_type="exact",
                    confidence_score=1.0,
                ):
                    alias_count += 1

            source_links = list(
                db.scalars(
                    select(FoodSourceLink).where(FoodSourceLink.food_item_id == food_item.id)
                ).all()
            )

            for link in source_links:
                source_record = db.scalar(
                    select(SourceFoodRecord)
                    .join(
                        IngestionRelease,
                        IngestionRelease.id == SourceFoodRecord.ingestion_release_id,
                    )
                    .where(
                        SourceFoodRecord.ingestion_release_id == link.ingestion_release_id,
                        SourceFoodRecord.source_record_key == link.source_record_key,
                    )
                )
                if source_record is None:
                    continue

                if upsert_food_alias(
                    db,
                    food_item_id=food_item.id,
                    alias_text=source_record.source_food_name,
                    alias_type="source_name",
                    confidence_score=1.0,
                ):
                    alias_count += 1

            if food_item.brand and food_item.display_name:
                branded_alias = f"{food_item.brand} {food_item.display_name}"
                if upsert_food_alias(
                    db,
                    food_item_id=food_item.id,
                    alias_text=branded_alias,
                    alias_type="synonym",
                    confidence_score=0.8,
                ):
                    alias_count += 1

        db.commit()
        print(
            f"Alias build completed successfully. "
            f"processed_food_items={len(food_items)}, alias_operations={alias_count}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()