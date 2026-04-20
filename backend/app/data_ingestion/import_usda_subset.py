from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data_ingestion.normalization import (
    build_source_slug,
    compute_sha256,
    extract_usda_core_nutrients,
    extract_usda_foods,
    extract_usda_micronutrients,
    get_or_create_data_source,
    get_or_create_ingestion_release,
    iter_usda_nutrients,
    load_json_file,
    normalize_text,
    upsert_food_alias,
)
from app.db.session import SessionLocal
from app.models.food_item import FoodItem
from app.models.food_source_link import FoodSourceLink
from app.models.ingestion_release import IngestionRelease
from app.models.nutrition_fact import NutritionFact
from app.models.source_food_record import SourceFoodRecord
from app.models.source_nutrient_record import SourceNutrientRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a USDA subset JSON file into raw source tables and the normalized catalog.",
    )
    parser.add_argument(
        "--json-path",
        type=str,
        required=True,
        help="Path to a USDA subset JSON file.",
    )
    parser.add_argument(
        "--source-version",
        type=str,
        default="local-json",
        help="Version label for this USDA ingestion release.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on the number of foods processed.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and stage the import but roll back at the end.",
    )
    return parser.parse_args()


def resolve_source_record_key(food: dict[str, Any]) -> str | None:
    raw_value = (
        food.get("fdcId")
        or food.get("fdc_id")
        or food.get("id")
        or food.get("source_record_key")
    )
    if raw_value is None:
        return None
    return str(raw_value).strip() or None


def resolve_food_name(food: dict[str, Any]) -> str | None:
    for key in ("description", "foodDescription", "name"):
        value = food.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def resolve_brand_name(food: dict[str, Any]) -> str | None:
    for key in ("brandOwner", "brandName", "brand_name"):
        value = food.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def upsert_source_food_record(
    db: Session,
    *,
    ingestion_release_id: str,
    source_record_key: str,
    source_food_name: str,
    brand_name: str | None,
    payload_json: dict[str, Any],
) -> SourceFoodRecord:
    record = db.scalar(
        select(SourceFoodRecord).where(
            SourceFoodRecord.ingestion_release_id == ingestion_release_id,
            SourceFoodRecord.source_record_key == source_record_key,
        )
    )
    normalized_hash = compute_sha256(
        {
            "source_record_key": source_record_key,
            "source_food_name": source_food_name,
            "brand_name": brand_name,
        }
    )

    if record is None:
        record = SourceFoodRecord(
            ingestion_release_id=ingestion_release_id,
            source_record_key=source_record_key,
            source_food_name=source_food_name,
            brand_name=brand_name,
            payload_json=payload_json,
            normalized_hash=normalized_hash,
        )
        db.add(record)
        db.flush()
        return record

    record.source_food_name = source_food_name
    record.brand_name = brand_name
    record.payload_json = payload_json
    record.normalized_hash = normalized_hash
    db.flush()
    return record


def replace_source_nutrients(
    db: Session,
    *,
    source_food_record_id: str,
    nutrients: list[dict[str, Any]],
) -> None:
    existing_rows = db.scalars(
        select(SourceNutrientRecord).where(
            SourceNutrientRecord.source_food_record_id == source_food_record_id
        )
    ).all()
    for row in existing_rows:
        db.delete(row)
    db.flush()

    for nutrient in nutrients:
        db.add(
            SourceNutrientRecord(
                source_food_record_id=source_food_record_id,
                nutrient_code=nutrient["nutrient_code"],
                nutrient_name=nutrient["nutrient_name"],
                amount=nutrient["amount"],
                unit=nutrient["unit"],
                payload_json=nutrient["payload_json"],
            )
        )
    db.flush()


def get_or_create_food_item_for_usda(
    db: Session,
    *,
    source_record_key: str,
    display_name: str,
    normalized_name: str,
    brand_name: str | None,
) -> FoodItem:
    existing_link = db.scalar(
        select(FoodSourceLink).where(
            FoodSourceLink.source_record_key == source_record_key
        )
    )
    if existing_link is not None:
        food_item = db.scalar(
            select(FoodItem).where(FoodItem.id == existing_link.food_item_id)
        )
        if food_item is not None:
            return food_item

    existing_food = db.scalar(
        select(FoodItem).where(
            FoodItem.source == "usda_fdc",
            FoodItem.normalized_name == normalized_name,
        )
    )
    if existing_food is not None:
        return existing_food

    food_item = FoodItem(
        name=display_name,
        slug=build_source_slug("usda", display_name, source_record_key),
        brand=brand_name,
        category="usda_import",
        description=f"Imported from USDA FDC source record {source_record_key}",
        default_serving_size_g=100.0,
        default_serving_label="100 g",
        source="usda_fdc",
        normalized_name=normalized_name,
        display_name=display_name,
        search_name=display_name,
        usage_count=0,
        popularity_score=0,
        is_active=True,
    )
    db.add(food_item)
    db.flush()
    return food_item


def upsert_nutrition_fact(
    db: Session,
    *,
    food_item_id: str,
    core_nutrients: dict[str, float | None],
    micronutrients_json: dict[str, float] | None,
) -> NutritionFact:
    nutrition = db.scalar(
        select(NutritionFact).where(NutritionFact.food_item_id == food_item_id)
    )
    if nutrition is None:
        nutrition = NutritionFact(
            food_item_id=food_item_id,
            calories_per_100g=float(core_nutrients["calories_per_100g"] or 0),
            protein_g_per_100g=float(core_nutrients["protein_g_per_100g"] or 0),
            carbs_g_per_100g=float(core_nutrients["carbs_g_per_100g"] or 0),
            fat_g_per_100g=float(core_nutrients["fat_g_per_100g"] or 0),
            fiber_g_per_100g=core_nutrients["fiber_g_per_100g"],
            sugar_g_per_100g=core_nutrients["sugar_g_per_100g"],
            sodium_mg_per_100g=core_nutrients["sodium_mg_per_100g"],
            micronutrients_json=micronutrients_json or None,
            source_quality="usda_subset",
        )
        db.add(nutrition)
        db.flush()
        return nutrition

    nutrition.calories_per_100g = float(core_nutrients["calories_per_100g"] or 0)
    nutrition.protein_g_per_100g = float(core_nutrients["protein_g_per_100g"] or 0)
    nutrition.carbs_g_per_100g = float(core_nutrients["carbs_g_per_100g"] or 0)
    nutrition.fat_g_per_100g = float(core_nutrients["fat_g_per_100g"] or 0)
    nutrition.fiber_g_per_100g = core_nutrients["fiber_g_per_100g"]
    nutrition.sugar_g_per_100g = core_nutrients["sugar_g_per_100g"]
    nutrition.sodium_mg_per_100g = core_nutrients["sodium_mg_per_100g"]
    nutrition.micronutrients_json = micronutrients_json or None
    nutrition.source_quality = "usda_subset"
    db.flush()
    return nutrition


def upsert_food_source_link(
    db: Session,
    *,
    food_item_id: str,
    data_source_id: str,
    ingestion_release_id: str,
    source_record_key: str,
) -> FoodSourceLink:
    link = db.scalar(
        select(FoodSourceLink).where(
            FoodSourceLink.food_item_id == food_item_id,
            FoodSourceLink.data_source_id == data_source_id,
            FoodSourceLink.ingestion_release_id == ingestion_release_id,
            FoodSourceLink.source_record_key == source_record_key,
        )
    )
    if link is None:
        link = FoodSourceLink(
            food_item_id=food_item_id,
            data_source_id=data_source_id,
            ingestion_release_id=ingestion_release_id,
            source_record_key=source_record_key,
            source_priority=1,
            is_primary=True,
        )
        db.add(link)
        db.flush()
        return link

    link.source_priority = 1
    link.is_primary = True
    db.flush()
    return link


def main() -> None:
    args = parse_args()
    payload = load_json_file(args.json_path)
    foods = extract_usda_foods(payload)
    if args.limit is not None:
        foods = foods[: args.limit]

    db = SessionLocal()
    try:
        data_source = get_or_create_data_source(db, source_code="USDA_FDC")
        release = get_or_create_ingestion_release(
            db,
            data_source_id=data_source.id,
            source_version=args.source_version,
            status="processing",
            metadata_json={"input_path": args.json_path},
        )
        release.started_at = datetime.now(timezone.utc)

        raw_count = 0
        normalized_count = 0
        skipped = 0

        for food in foods:
            source_record_key = resolve_source_record_key(food)
            display_name = resolve_food_name(food)
            brand_name = resolve_brand_name(food)

            if not source_record_key or not display_name:
                skipped += 1
                continue

            normalized_name = normalize_text(display_name)
            source_record = upsert_source_food_record(
                db,
                ingestion_release_id=release.id,
                source_record_key=source_record_key,
                source_food_name=display_name,
                brand_name=brand_name,
                payload_json=food,
            )
            raw_count += 1

            nutrients = iter_usda_nutrients(food)
            replace_source_nutrients(
                db,
                source_food_record_id=source_record.id,
                nutrients=nutrients,
            )

            core_nutrients = extract_usda_core_nutrients(food)
            required = (
                core_nutrients["calories_per_100g"],
                core_nutrients["protein_g_per_100g"],
                core_nutrients["carbs_g_per_100g"],
                core_nutrients["fat_g_per_100g"],
            )
            if any(value is None for value in required):
                skipped += 1
                continue

            food_item = get_or_create_food_item_for_usda(
                db,
                source_record_key=source_record_key,
                display_name=display_name,
                normalized_name=normalized_name,
                brand_name=brand_name,
            )
            food_item.name = display_name
            food_item.display_name = display_name
            food_item.normalized_name = normalized_name
            food_item.search_name = display_name
            if brand_name:
                food_item.brand = brand_name

            upsert_nutrition_fact(
                db,
                food_item_id=food_item.id,
                core_nutrients=core_nutrients,
                micronutrients_json=extract_usda_micronutrients(food),
            )
            upsert_food_source_link(
                db,
                food_item_id=food_item.id,
                data_source_id=data_source.id,
                ingestion_release_id=release.id,
                source_record_key=source_record_key,
            )

            upsert_food_alias(
                db,
                food_item_id=food_item.id,
                alias_text=display_name,
                alias_type="exact",
                confidence_score=1.0,
            )
            upsert_food_alias(
                db,
                food_item_id=food_item.id,
                alias_text=display_name,
                alias_type="source_name",
                confidence_score=1.0,
            )

            normalized_count += 1

        release.raw_record_count = raw_count
        release.normalized_record_count = normalized_count
        release.status = "published"
        release.published_at = datetime.now(timezone.utc)

        if args.dry_run:
            db.rollback()
            print(
                f"Dry run complete. raw_count={raw_count}, "
                f"normalized_count={normalized_count}, skipped={skipped}"
            )
            return

        db.commit()
        print(
            f"USDA subset import completed successfully. "
            f"raw_count={raw_count}, normalized_count={normalized_count}, skipped={skipped}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()