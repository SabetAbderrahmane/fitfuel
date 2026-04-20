from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.data_source import DataSource
from app.models.food_alias import FoodAlias
from app.models.ingestion_release import IngestionRelease


WHITESPACE_RE = re.compile(r"\s+")
SLUG_SAFE_RE = re.compile(r"[^a-z0-9]+")

DEFAULT_SOURCE_DEFINITIONS: dict[str, dict[str, str]] = {
    "USDA_FDC": {
        "display_name": "USDA FoodData Central",
        "source_type": "nutrition_catalog",
        "license_name": "USDA / public",
        "homepage_url": "https://fdc.nal.usda.gov/",
    },
    "OPEN_FOOD_FACTS": {
        "display_name": "Open Food Facts",
        "source_type": "nutrition_catalog",
        "license_name": "Open Database License",
        "homepage_url": "https://world.openfoodfacts.org/",
    },
    "FOOD101": {
        "display_name": "Food-101",
        "source_type": "classifier_labels",
        "license_name": "research dataset",
        "homepage_url": "https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/",
    },
    "UEC_FOOD_256": {
        "display_name": "UEC FOOD-256",
        "source_type": "classifier_labels",
        "license_name": "research dataset",
        "homepage_url": "http://foodcam.mobi/dataset256.html",
    },
}


def collapse_whitespace(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value.strip())


def normalize_text(value: str) -> str:
    normalized = collapse_whitespace(value).lower()
    normalized = normalized.replace("_", " ").replace("-", " ")
    return collapse_whitespace(normalized)


def slugify(value: str, max_length: int = 120) -> str:
    text = normalize_text(value)
    text = SLUG_SAFE_RE.sub("-", text).strip("-")
    text = text or "food"
    return text[:max_length].strip("-") or "food"


def build_source_slug(prefix: str, display_name: str, source_record_key: str) -> str:
    base = slugify(display_name, max_length=80)
    key_slug = slugify(source_record_key, max_length=32)
    return f"{slugify(prefix, max_length=20)}-{key_slug}-{base}"[:255]


def compute_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_or_create_data_source(
    db: Session,
    *,
    source_code: str,
    display_name: str | None = None,
    source_type: str | None = None,
    license_name: str | None = None,
    homepage_url: str | None = None,
) -> DataSource:
    source = db.scalar(
        select(DataSource).where(DataSource.source_code == source_code)
    )
    if source is not None:
        if display_name:
            source.display_name = display_name
        if source_type:
            source.source_type = source_type
        if license_name is not None:
            source.license_name = license_name
        if homepage_url is not None:
            source.homepage_url = homepage_url
        return source

    defaults = DEFAULT_SOURCE_DEFINITIONS.get(source_code, {})
    source = DataSource(
        source_code=source_code,
        display_name=display_name or defaults.get("display_name", source_code),
        source_type=source_type or defaults.get("source_type", "external"),
        license_name=license_name if license_name is not None else defaults.get("license_name"),
        homepage_url=homepage_url if homepage_url is not None else defaults.get("homepage_url"),
        is_active=True,
    )
    db.add(source)
    db.flush()
    return source


def get_or_create_ingestion_release(
    db: Session,
    *,
    data_source_id: str,
    source_version: str,
    status: str = "draft",
    metadata_json: dict[str, Any] | None = None,
) -> IngestionRelease:
    release = db.scalar(
        select(IngestionRelease).where(
            IngestionRelease.data_source_id == data_source_id,
            IngestionRelease.source_version == source_version,
        )
    )
    if release is not None:
        if metadata_json is not None:
            release.metadata_json = metadata_json
        release.status = status
        return release

    release = IngestionRelease(
        data_source_id=data_source_id,
        source_version=source_version,
        status=status,
        metadata_json=metadata_json,
    )
    db.add(release)
    db.flush()
    return release


def upsert_food_alias(
    db: Session,
    *,
    food_item_id: str,
    alias_text: str,
    alias_type: str,
    language_code: str = "en",
    confidence_score: float = 1.0,
) -> FoodAlias | None:
    alias_text = collapse_whitespace(alias_text)
    normalized_alias = normalize_text(alias_text)
    if not normalized_alias:
        return None

    existing = db.scalar(
        select(FoodAlias).where(
            FoodAlias.food_item_id == food_item_id,
            FoodAlias.normalized_alias == normalized_alias,
            FoodAlias.alias_type == alias_type,
        )
    )
    if existing is not None:
        existing.alias_text = alias_text
        existing.language_code = language_code
        existing.confidence_score = confidence_score
        return existing

    alias = FoodAlias(
        food_item_id=food_item_id,
        alias_text=alias_text,
        normalized_alias=normalized_alias,
        alias_type=alias_type,
        language_code=language_code,
        confidence_score=confidence_score,
    )
    db.add(alias)
    db.flush()
    return alias


def clear_existing_source_nutrients(db: Session, *, source_food_record_id: str) -> None:
    db.execute(
        delete_source_nutrient_records_stmt(source_food_record_id)
    )


def delete_source_nutrient_records_stmt(source_food_record_id: str):
    from app.models.source_nutrient_record import SourceNutrientRecord

    return delete(SourceNutrientRecord).where(
        SourceNutrientRecord.source_food_record_id == source_food_record_id
    )


def load_json_file(path: str | Path) -> Any:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_usda_foods(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        foods = payload.get("foods")
        if isinstance(foods, list):
            return [item for item in foods if isinstance(item, dict)]

        results = payload.get("FoundationFoods") or payload.get("foundationFoods")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]

    raise ValueError(
        "Unsupported USDA subset format. Expected either a JSON array of foods "
        "or a JSON object with a 'foods' list."
    )


def display_label_from_raw(raw_label: str) -> str:
    label = collapse_whitespace(raw_label.replace("_", " ").replace("-", " "))
    return label


def get_nested(mapping: dict[str, Any], *path: str) -> Any:
    current: Any = mapping
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def iter_usda_nutrients(food: dict[str, Any]) -> list[dict[str, Any]]:
    raw_nutrients = food.get("foodNutrients") or food.get("food_nutrients") or []
    result: list[dict[str, Any]] = []

    for nutrient in raw_nutrients:
        if not isinstance(nutrient, dict):
            continue

        nutrient_name = (
            nutrient.get("nutrientName")
            or nutrient.get("nutrient_name")
            or nutrient.get("name")
            or get_nested(nutrient, "nutrient", "name")
        )
        nutrient_code = (
            nutrient.get("nutrientNumber")
            or nutrient.get("nutrient_number")
            or nutrient.get("number")
            or get_nested(nutrient, "nutrient", "number")
        )
        amount = nutrient.get("amount")
        if amount is None:
            amount = nutrient.get("value")
        unit = (
            nutrient.get("unitName")
            or nutrient.get("unit")
            or get_nested(nutrient, "nutrient", "unitName")
        )

        try:
            amount_value = float(amount) if amount is not None else None
        except (TypeError, ValueError):
            amount_value = None

        result.append(
            {
                "nutrient_name": nutrient_name,
                "nutrient_code": str(nutrient_code) if nutrient_code is not None else None,
                "amount": amount_value,
                "unit": unit,
                "payload_json": nutrient,
            }
        )

    return result


def extract_usda_core_nutrients(food: dict[str, Any]) -> dict[str, float | None]:
    nutrients = iter_usda_nutrients(food)

    def match_name(name: str | None) -> str:
        return normalize_text(name or "")

    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    fiber: float | None = None
    sugar: float | None = None
    sodium: float | None = None

    for nutrient in nutrients:
        code = nutrient["nutrient_code"]
        name = match_name(nutrient["nutrient_name"])
        amount = nutrient["amount"]
        unit = (nutrient["unit"] or "").strip().lower()

        if amount is None:
            continue

        if calories is None and (
            code == "208"
            or name == "energy"
            or "energy" in name
        ):
            if unit == "kj":
                calories = round(amount / 4.184, 4)
            else:
                calories = amount
            continue

        if protein is None and (code == "203" or "protein" in name):
            protein = amount
            continue

        if carbs is None and (code == "205" or "carbohydrate" in name):
            carbs = amount
            continue

        if fat is None and (
            code == "204"
            or "total lipid" in name
            or name == "fat"
            or "total fat" in name
        ):
            fat = amount
            continue

        if fiber is None and (code == "291" or "fiber" in name):
            fiber = amount
            continue

        if sugar is None and (code == "269" or "sugar" in name):
            sugar = amount
            continue

        if sodium is None and (code == "307" or "sodium" in name):
            sodium = amount
            continue

    return {
        "calories_per_100g": calories,
        "protein_g_per_100g": protein,
        "carbs_g_per_100g": carbs,
        "fat_g_per_100g": fat,
        "fiber_g_per_100g": fiber,
        "sugar_g_per_100g": sugar,
        "sodium_mg_per_100g": sodium,
    }


def extract_usda_micronutrients(food: dict[str, Any]) -> dict[str, float]:
    nutrients = iter_usda_nutrients(food)
    micronutrients: dict[str, float] = {}

    core_codes = {"203", "204", "205", "208", "269", "291", "307"}
    for nutrient in nutrients:
        code = nutrient["nutrient_code"]
        name = display_label_from_raw(nutrient["nutrient_name"] or "")
        amount = nutrient["amount"]
        unit = (nutrient["unit"] or "").strip()

        if amount is None or not name:
            continue
        if code in core_codes:
            continue

        key = normalize_text(name).replace(" ", "_")
        if unit:
            key = f"{key}_{unit.lower()}"
        micronutrients[key] = amount

    return micronutrients