from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable

from rapidfuzz import fuzz
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap
from app.models.food_alias import FoodAlias
from app.models.food_item import FoodItem


@dataclass(slots=True)
class MappingCandidate:
    food_item_id: str
    match_confidence: float
    map_type: str
    requires_user_confirmation: bool
    ranking_hint: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build classifier_label_food_maps from classifier labels and the normalized food catalog.",
    )
    parser.add_argument(
        "--label-set-name",
        type=str,
        default=None,
        help="Optional label set filter, e.g. food101.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit for incremental runs.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum number of mappings to keep per classifier label.",
    )
    parser.add_argument(
        "--min-fuzzy-score",
        type=float,
        default=88.0,
        help="Minimum RapidFuzz token_sort_ratio score to keep a fuzzy candidate.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build mappings but roll back instead of committing.",
    )
    return parser.parse_args()


def _alias_type_weight(alias_type: str) -> float:
    weights = {
        "exact": 1.00,
        "source_name": 0.98,
        "classifier_label": 0.97,
        "user_correction": 0.96,
        "synonym": 0.94,
    }
    return weights.get(alias_type, 0.90)


def _candidate_sort_key(candidate: MappingCandidate) -> tuple[float, int]:
    return (-candidate.match_confidence, candidate.ranking_hint)


def _dedupe_candidates(candidates: Iterable[MappingCandidate]) -> list[MappingCandidate]:
    by_food_item: dict[str, MappingCandidate] = {}
    for candidate in candidates:
        existing = by_food_item.get(candidate.food_item_id)
        if existing is None or _candidate_sort_key(candidate) < _candidate_sort_key(existing):
            by_food_item[candidate.food_item_id] = candidate
    return list(by_food_item.values())


def _build_exact_alias_candidates(
    label: ClassifierLabel,
    aliases: list[FoodAlias],
) -> list[MappingCandidate]:
    matches: list[MappingCandidate] = []

    for alias in aliases:
        if alias.normalized_alias != label.normalized_label:
            continue

        weight = _alias_type_weight(alias.alias_type)
        requires_confirmation = alias.alias_type not in {"exact", "source_name"}

        matches.append(
            MappingCandidate(
                food_item_id=alias.food_item_id,
                match_confidence=round(weight, 4),
                map_type="exact_alias",
                requires_user_confirmation=requires_confirmation,
                ranking_hint=10,
            )
        )

    return matches


def _build_exact_name_candidates(
    label: ClassifierLabel,
    food_items: list[FoodItem],
) -> list[MappingCandidate]:
    matches: list[MappingCandidate] = []

    for food_item in food_items:
        if food_item.normalized_name != label.normalized_label:
            continue

        matches.append(
            MappingCandidate(
                food_item_id=food_item.id,
                match_confidence=0.97,
                map_type="canonical_exact",
                requires_user_confirmation=False,
                ranking_hint=20,
            )
        )

    return matches


def _build_fuzzy_alias_candidates(
    label: ClassifierLabel,
    aliases: list[FoodAlias],
    *,
    min_fuzzy_score: float,
) -> list[MappingCandidate]:
    matches: list[MappingCandidate] = []

    for alias in aliases:
        score = float(
            fuzz.token_sort_ratio(label.normalized_label, alias.normalized_alias)
        )
        if score < min_fuzzy_score:
            continue

        confidence = round((score / 100.0) * _alias_type_weight(alias.alias_type) * 0.93, 4)

        matches.append(
            MappingCandidate(
                food_item_id=alias.food_item_id,
                match_confidence=confidence,
                map_type="fuzzy_alias",
                requires_user_confirmation=True,
                ranking_hint=30,
            )
        )

    return matches


def _build_fuzzy_name_candidates(
    label: ClassifierLabel,
    food_items: list[FoodItem],
    *,
    min_fuzzy_score: float,
) -> list[MappingCandidate]:
    matches: list[MappingCandidate] = []

    for food_item in food_items:
        score = float(
            fuzz.token_sort_ratio(label.normalized_label, food_item.normalized_name)
        )
        if score < min_fuzzy_score:
            continue

        confidence = round((score / 100.0) * 0.90, 4)

        matches.append(
            MappingCandidate(
                food_item_id=food_item.id,
                match_confidence=confidence,
                map_type="fuzzy_food_item",
                requires_user_confirmation=True,
                ranking_hint=40,
            )
        )

    return matches


def _rank_candidates(
    label: ClassifierLabel,
    food_items: list[FoodItem],
    aliases: list[FoodAlias],
    *,
    min_fuzzy_score: float,
    top_k: int,
) -> list[MappingCandidate]:
    candidates: list[MappingCandidate] = []
    candidates.extend(_build_exact_alias_candidates(label, aliases))
    candidates.extend(_build_exact_name_candidates(label, food_items))
    candidates.extend(
        _build_fuzzy_alias_candidates(
            label,
            aliases,
            min_fuzzy_score=min_fuzzy_score,
        )
    )
    candidates.extend(
        _build_fuzzy_name_candidates(
            label,
            food_items,
            min_fuzzy_score=min_fuzzy_score,
        )
    )

    deduped = _dedupe_candidates(candidates)
    deduped.sort(key=_candidate_sort_key)

    if len(deduped) > 1:
        for candidate in deduped:
            if candidate.match_confidence < 0.995:
                candidate.requires_user_confirmation = True

    return deduped[:top_k]


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        label_statement = (
            select(ClassifierLabel)
            .where(ClassifierLabel.is_active.is_(True))
            .order_by(ClassifierLabel.label_set_name.asc(), ClassifierLabel.normalized_label.asc())
        )
        if args.label_set_name:
            label_statement = label_statement.where(
                ClassifierLabel.label_set_name == args.label_set_name
            )
        if args.limit:
            label_statement = label_statement.limit(args.limit)

        labels = list(db.scalars(label_statement).all())

        food_items = list(
            db.scalars(
                select(FoodItem)
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.normalized_name.asc())
            ).all()
        )

        aliases = list(
            db.scalars(
                select(FoodAlias)
                .options(selectinload(FoodAlias.food_item))
                .join(FoodItem, FoodItem.id == FoodAlias.food_item_id)
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodAlias.normalized_alias.asc())
            ).all()
        )

        total_labels = len(labels)
        mapped_labels = 0
        unmapped_labels = 0
        mapping_rows_written = 0

        for label in labels:
            candidates = _rank_candidates(
                label,
                food_items,
                aliases,
                min_fuzzy_score=args.min_fuzzy_score,
                top_k=max(1, args.top_k),
            )

            db.execute(
                delete(ClassifierLabelFoodMap).where(
                    ClassifierLabelFoodMap.classifier_label_id == label.id
                )
            )

            if not candidates:
                unmapped_labels += 1
                continue

            mapped_labels += 1

            for index, candidate in enumerate(candidates, start=1):
                db.add(
                    ClassifierLabelFoodMap(
                        classifier_label_id=label.id,
                        food_item_id=candidate.food_item_id,
                        map_type=candidate.map_type,
                        ranking=index,
                        match_confidence=candidate.match_confidence,
                        requires_user_confirmation=candidate.requires_user_confirmation,
                    )
                )
                mapping_rows_written += 1

        if args.dry_run:
            db.rollback()
            print(
                f"Dry run complete. total_labels={total_labels}, "
                f"mapped_labels={mapped_labels}, unmapped_labels={unmapped_labels}, "
                f"mapping_rows_written={mapping_rows_written}"
            )
            return

        db.commit()
        print(
            f"Classifier label mapping build completed successfully. "
            f"total_labels={total_labels}, mapped_labels={mapped_labels}, "
            f"unmapped_labels={unmapped_labels}, mapping_rows_written={mapping_rows_written}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()