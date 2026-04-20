from __future__ import annotations

import argparse
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.data_ingestion.normalization import (
    display_label_from_raw,
    get_or_create_data_source,
    get_or_create_ingestion_release,
    load_json_file,
    normalize_text,
)
from app.db.session import SessionLocal
from app.models.classifier_label import ClassifierLabel


DEFAULT_TEST_LABELS = [
    "banana",
    "apple_pie",
    "fried_rice",
    "grilled_salmon",
    "omelette",
]


def load_labels(path: str | None) -> list[str]:
    if path:
        file_path = Path(path)
    elif settings.vision_class_names_path.strip():
        file_path = Path(settings.vision_class_names_path)
    else:
        return DEFAULT_TEST_LABELS.copy()

    if not file_path.exists():
        raise FileNotFoundError(f"Labels file not found: {file_path}")

    if file_path.suffix.lower() == ".json":
        payload = load_json_file(file_path)
        if isinstance(payload, list):
            return [str(item).strip() for item in payload if str(item).strip()]
        if isinstance(payload, dict):
            labels = payload.get("labels")
            if isinstance(labels, list):
                return [str(item).strip() for item in labels if str(item).strip()]
        raise ValueError("Unsupported JSON labels file format.")

    with file_path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed classifier labels into classifier_labels.",
    )
    parser.add_argument(
        "--labels-file",
        type=str,
        default=None,
        help="Optional path to a newline-delimited or JSON labels file.",
    )
    parser.add_argument(
        "--label-set-name",
        type=str,
        default="food101",
        help="Logical label set name to store in classifier_labels.",
    )
    parser.add_argument(
        "--source-code",
        type=str,
        default="FOOD101",
        help="Data source code to register for this classifier label seed.",
    )
    parser.add_argument(
        "--source-version",
        type=str,
        default="v1",
        help="Ingestion release version label for provenance tracking.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labels = load_labels(args.labels_file)

    if not labels:
        raise ValueError("No classifier labels were provided.")

    db = SessionLocal()
    try:
        data_source = get_or_create_data_source(
            db,
            source_code=args.source_code,
        )
        get_or_create_ingestion_release(
            db,
            data_source_id=data_source.id,
            source_version=args.source_version,
            status="published",
            metadata_json={
                "label_set_name": args.label_set_name,
                "label_count": len(labels),
            },
        )

        created = 0
        updated = 0

        for raw_label in labels:
            normalized_label = normalize_text(raw_label)
            display_label = display_label_from_raw(raw_label)

            existing = db.scalar(
                select(ClassifierLabel).where(
                    ClassifierLabel.label_set_name == args.label_set_name,
                    ClassifierLabel.normalized_label == normalized_label,
                )
            )
            if existing is not None:
                existing.raw_label = raw_label
                existing.display_label = display_label
                existing.is_active = True
                updated += 1
                continue

            label = ClassifierLabel(
                label_set_name=args.label_set_name,
                raw_label=raw_label,
                normalized_label=normalized_label,
                display_label=display_label,
                is_active=True,
            )
            db.add(label)
            created += 1

        db.commit()
        print(
            f"Classifier labels seeded successfully. "
            f"created={created}, updated={updated}, total_input={len(labels)}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()