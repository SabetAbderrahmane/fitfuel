from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap
from app.models.food_item import FoodItem
from app.models.nutrition_fact import NutritionFact


LABEL_SET_NAME = "food101_subset_resnet50"
DEMO_SOURCE = "cv_demo_estimate"
REPORT_PATH = Path(__file__).resolve().parents[2] / "docs" / "cv-label-food-map-report.md"
REPORT_NOTE = "Demo estimate; not image-derived portion estimation."


@dataclass(frozen=True)
class CvDemoFoodSeed:
    raw_label: str
    display_name: str
    calories_per_100g: float
    protein_g_per_100g: float
    carbs_g_per_100g: float
    fat_g_per_100g: float
    description: str


CV_DEMO_FOODS = (
    CvDemoFoodSeed("apple_pie", "Apple Pie", 237, 2.4, 34.0, 11.0, "CV demo estimate for apple pie."),
    CvDemoFoodSeed("caesar_salad", "Caesar Salad", 180, 5.0, 7.0, 15.0, "CV demo estimate for caesar salad."),
    CvDemoFoodSeed("chicken_curry", "Chicken Curry", 140, 11.0, 6.0, 8.0, "CV demo estimate for chicken curry."),
    CvDemoFoodSeed("fried_rice", "Fried Rice", 165, 4.0, 28.0, 4.0, "CV demo estimate for fried rice."),
    CvDemoFoodSeed("grilled_salmon", "Grilled Salmon", 206, 22.0, 0.0, 12.0, "CV demo estimate for grilled salmon."),
    CvDemoFoodSeed("omelette", "Omelette", 154, 11.0, 1.0, 12.0, "CV demo estimate for omelette."),
    CvDemoFoodSeed("pizza", "Pizza", 266, 11.0, 33.0, 10.0, "CV demo estimate for pizza."),
    CvDemoFoodSeed("ramen", "Ramen", 110, 4.0, 15.0, 4.0, "CV demo estimate for ramen."),
    CvDemoFoodSeed("steak", "Steak", 271, 25.0, 0.0, 19.0, "CV demo estimate for steak."),
    CvDemoFoodSeed("sushi", "Sushi", 145, 6.0, 28.0, 1.0, "CV demo estimate for sushi."),
)


def normalize_text(value: str) -> str:
    normalized = value.strip().lower().replace("_", " ").replace("-", " ")
    return " ".join(normalized.split())


def slugify(value: str) -> str:
    normalized = normalize_text(value)
    return normalized.replace(" ", "-")


def find_or_create_classifier_label(db: Session, seed: CvDemoFoodSeed) -> ClassifierLabel:
    normalized = normalize_text(seed.raw_label)
    label = db.scalar(
        select(ClassifierLabel).where(
            ClassifierLabel.label_set_name == LABEL_SET_NAME,
            ClassifierLabel.normalized_label == normalized,
        )
    )
    if label is None:
        label = ClassifierLabel(
            label_set_name=LABEL_SET_NAME,
            raw_label=seed.raw_label,
            normalized_label=normalized,
            display_label=seed.display_name,
            is_active=True,
        )
        db.add(label)
        db.flush()
        return label

    label.raw_label = seed.raw_label
    label.display_label = seed.display_name
    label.is_active = True
    return label


def find_or_create_demo_food_item(db: Session, seed: CvDemoFoodSeed) -> FoodItem:
    normalized_name = normalize_text(seed.display_name)
    food_item = db.scalar(
        select(FoodItem).where(
            FoodItem.source == DEMO_SOURCE,
            FoodItem.normalized_name == normalized_name,
        )
    )
    if food_item is None:
        food_item = FoodItem(
            name=seed.display_name,
            slug=f"cv-demo-{slugify(seed.display_name)}",
            source=DEMO_SOURCE,
            normalized_name=normalized_name,
            display_name=seed.display_name,
            search_name=f"{normalized_name} {normalize_text(seed.raw_label)}",
            category="cv_demo_food",
            description=seed.description,
            default_serving_size_g=100.0,
            default_serving_label="100 g demo serving",
            is_active=True,
        )
        db.add(food_item)
        db.flush()
    else:
        food_item.name = seed.display_name
        food_item.source = DEMO_SOURCE
        food_item.normalized_name = normalized_name
        food_item.display_name = seed.display_name
        food_item.search_name = f"{normalized_name} {normalize_text(seed.raw_label)}"
        food_item.category = "cv_demo_food"
        food_item.description = seed.description
        food_item.default_serving_size_g = 100.0
        food_item.default_serving_label = "100 g demo serving"
        food_item.is_active = True

    ensure_demo_nutrition(food_item, seed)
    return food_item


def ensure_demo_nutrition(food_item: FoodItem, seed: CvDemoFoodSeed) -> NutritionFact:
    nutrition = food_item.nutrition_fact
    if nutrition is None:
        nutrition = NutritionFact(food_item_id=food_item.id)
        food_item.nutrition_fact = nutrition

    nutrition.calories_per_100g = seed.calories_per_100g
    nutrition.protein_g_per_100g = seed.protein_g_per_100g
    nutrition.carbs_g_per_100g = seed.carbs_g_per_100g
    nutrition.fat_g_per_100g = seed.fat_g_per_100g
    nutrition.source_quality = DEMO_SOURCE
    return nutrition


def find_existing_map(
    db: Session,
    classifier_label_id: str,
    food_item_id: str,
) -> ClassifierLabelFoodMap | None:
    return db.scalar(
        select(ClassifierLabelFoodMap).where(
            ClassifierLabelFoodMap.classifier_label_id == classifier_label_id,
            ClassifierLabelFoodMap.food_item_id == food_item_id,
        )
    )


def prefer_demo_mapping(
    db: Session,
    classifier_label: ClassifierLabel,
    food_item: FoodItem,
) -> ClassifierLabelFoodMap:
    existing_maps = list(
        db.scalars(
            select(ClassifierLabelFoodMap).where(
                ClassifierLabelFoodMap.classifier_label_id == classifier_label.id,
            )
        ).all()
    )
    for existing_map in existing_maps:
        if existing_map.food_item_id != food_item.id:
            existing_map.ranking = max(existing_map.ranking or 1, 2)
            existing_map.requires_user_confirmation = True

    mapping = find_existing_map(db, classifier_label.id, food_item.id)
    if mapping is None:
        mapping = ClassifierLabelFoodMap(
            classifier_label_id=classifier_label.id,
            food_item_id=food_item.id,
        )
        db.add(mapping)

    mapping.map_type = "cv_demo_estimate"
    mapping.ranking = 1
    mapping.match_confidence = 1.0
    mapping.requires_user_confirmation = False
    return mapping


def build_report_row(
    seed: CvDemoFoodSeed,
    food_item: FoodItem,
) -> dict[str, str | float]:
    nutrition = food_item.nutrition_fact
    if nutrition is None:
        raise RuntimeError(f"Missing nutrition for seeded CV demo item: {food_item.name}")
    return {
        "label": seed.raw_label,
        "status": "mapped",
        "food_item_id": food_item.id,
        "food_item_name": food_item.display_name or food_item.name,
        "source": food_item.source,
        "calories": nutrition.calories_per_100g,
        "protein": nutrition.protein_g_per_100g,
        "carbs": nutrition.carbs_g_per_100g,
        "fat": nutrition.fat_g_per_100g,
        "note": REPORT_NOTE,
    }


def write_report(rows: list[dict[str, str | float]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CV Label To Food Item Mapping Report",
        "",
        "Generated by `python -m app.scripts.seed_cv_label_food_maps`.",
        "",
        "| Classifier label | Mapping status | FoodItem id | FoodItem name | Source | Calories/100g | Protein/100g | Carbs/100g | Fat/100g | Note |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {status} | {food_item_id} | {food_item_name} | {source} | {calories} | {protein} | {carbs} | {fat} | {note} |".format(
                **row
            )
        )
    lines.append("")
    lines.append("All supported CV labels map to dedicated `cv_demo_estimate` catalog items.")
    lines.append("These values support thesis/demo calorie estimates and are not medical-grade nutrition data.")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def seed_cv_label_food_maps(db: Session) -> list[dict[str, str | float]]:
    report_rows: list[dict[str, str | float]] = []

    for seed in CV_DEMO_FOODS:
        classifier_label = find_or_create_classifier_label(db, seed)
        food_item = find_or_create_demo_food_item(db, seed)
        prefer_demo_mapping(db, classifier_label, food_item)
        report_rows.append(build_report_row(seed, food_item))

    db.commit()
    write_report(report_rows)
    return report_rows


def main() -> None:
    db = SessionLocal()
    try:
        rows = seed_cv_label_food_maps(db)
    finally:
        db.close()

    mapped = sum(1 for row in rows if row["status"] == "mapped")
    print(f"Seeded classifier labels: {len(rows)}")
    print(f"Mapped labels: {mapped}")
    print("Unmapped labels: 0")
    print(f"Demo catalog source: {DEMO_SOURCE}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
