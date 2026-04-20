from __future__ import annotations

import argparse

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report classifier label mapping coverage.",
    )
    parser.add_argument(
        "--label-set-name",
        type=str,
        default=None,
        help="Optional label set filter, e.g. food101.",
    )
    parser.add_argument(
        "--show-unmapped",
        type=int,
        default=20,
        help="How many unmapped labels to print.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        total_labels_stmt = select(func.count(ClassifierLabel.id)).where(
            ClassifierLabel.is_active.is_(True)
        )
        if args.label_set_name:
            total_labels_stmt = total_labels_stmt.where(
                ClassifierLabel.label_set_name == args.label_set_name
            )

        total_labels = db.scalar(total_labels_stmt) or 0

        mapped_labels_stmt = (
            select(func.count(func.distinct(ClassifierLabelFoodMap.classifier_label_id)))
            .select_from(ClassifierLabelFoodMap)
            .join(
                ClassifierLabel,
                ClassifierLabel.id == ClassifierLabelFoodMap.classifier_label_id,
            )
            .where(ClassifierLabel.is_active.is_(True))
        )
        if args.label_set_name:
            mapped_labels_stmt = mapped_labels_stmt.where(
                ClassifierLabel.label_set_name == args.label_set_name
            )

        mapped_labels = db.scalar(mapped_labels_stmt) or 0
        unmapped_labels = total_labels - mapped_labels

        unmapped_stmt = (
            select(ClassifierLabel.label_set_name, ClassifierLabel.raw_label)
            .outerjoin(
                ClassifierLabelFoodMap,
                ClassifierLabel.id == ClassifierLabelFoodMap.classifier_label_id,
            )
            .where(
                ClassifierLabel.is_active.is_(True),
                ClassifierLabelFoodMap.id.is_(None),
            )
            .order_by(ClassifierLabel.label_set_name.asc(), ClassifierLabel.raw_label.asc())
            .limit(max(0, args.show_unmapped))
        )
        if args.label_set_name:
            unmapped_stmt = unmapped_stmt.where(
                ClassifierLabel.label_set_name == args.label_set_name
            )

        unmapped_rows = list(db.execute(unmapped_stmt).all())

        print(
            f"Classifier mapping coverage: total_labels={total_labels}, "
            f"mapped_labels={mapped_labels}, unmapped_labels={unmapped_labels}"
        )

        if unmapped_rows:
            print("Top unmapped labels:")
            for row in unmapped_rows:
                print(f"- [{row.label_set_name}] {row.raw_label}")
    finally:
        db.close()


if __name__ == "__main__":
    main()