from __future__ import annotations

import argparse
import ast
import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from rapidfuzz import fuzz, process
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models.food_item import FoodItem
from app.models.meal_template import MealTemplate
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient


SOURCE_CODE = "recipenlg_thesis"
REPORT_PATH = Path(__file__).resolve().parents[2] / "docs" / "recipenlg-import-report.md"
DISCLAIMER = "Imported from RecipeNLG for thesis/demo use only."

SCENARIO_BUCKETS = [
    "breakfast",
    "lunch",
    "dinner",
    "high_protein",
    "vegetarian_candidate",
    "halal_candidate",
    "gluten_free_candidate",
    "dairy_free_candidate",
    "egg_free_candidate",
    "peanut_free_candidate",
    "low_carb",
    "snack",
    "general_balanced",
    "vegan_candidate",
]

SLOT_ORDER = ("breakfast", "lunch", "dinner", "snack")

SLOT_CALORIE_RANGES = {
    "breakfast": (250, 700),
    "lunch": (350, 850),
    "dinner": (350, 900),
    "snack": (100, 400),
}

BREAKFAST_TERMS = {
    "oat",
    "oats",
    "oatmeal",
    "pancake",
    "pancakes",
    "french toast",
    "toast",
    "egg breakfast",
    "omelet",
    "omelette",
    "smoothie",
    "granola",
    "cereal",
    "yogurt",
    "banana",
    "breakfast",
    "muffin",
}

BREAKFAST_INGREDIENT_TERMS = {
    "oat",
    "oats",
    "oatmeal",
    "granola",
}

SAVORY_NON_BREAKFAST_TITLE_TERMS = {
    "barbecue",
    "bbq",
    "chicken",
    "tuna",
    "salmon",
    "steak",
    "beef",
    "pork",
    "ham",
    "sausage",
    "salad",
    "casserole",
}

HEALTHY_SNACK_TERMS = {
    "fruit salad",
    "yogurt",
    "smoothie",
    "protein shake",
    "boiled egg",
    "apple",
    "banana",
    "cottage cheese",
    "nuts",
    "hummus",
}

DESSERT_TITLE_TERMS = {
    "cookie",
    "cookies",
    "cake",
    "shortbread",
    "candy",
    "fudge",
    "pie",
    "brownie",
    "bars",
    "frosting",
    "icing",
    "pudding",
    "dessert",
    "sweet",
    "cupcake",
    "cheesecake",
    "ice cream",
    "sundae",
    "sherbet",
    "sorbet",
    "cobbler",
    "crisp",
    "crumble",
    "mousse",
    "trifle",
    "tart",
    "banana split",
    "gelatin",
    "jello",
    "marshmallow",
    "whipped",
    "frozen cherry",
    "almond roca",
    "almond roco",
    "roca",
    "roco",
}

LOW_QUALITY_MEAL_TITLE_TERMS = {
    "homemade noodles",
    "noodles",
    "bread",
    "rolls",
    "biscuit",
    "biscuits",
    "scone",
    "scones",
    "dough",
    "batter",
    "sauce",
    "dressing",
    "marinade",
    "seasoning",
    "mix",
    "spread",
    "dip",
    "cornbread",
    "dump salad",
    "roll-up",
    "roll-ups",
    "potatoes",
    "potato salad",
    "potato bake",
    "seashells",
    "cheese sandwich",
    "cheese sandwiches",
    "grilled cheese",
}

MINOR_UNMATCHED_INGREDIENTS = {
    "vanilla",
    "pepper",
    "cinnamon",
    "baking powder",
    "baking soda",
    "nutmeg",
    "parsley",
    "paprika",
    "salt",
    "water",
    "boiling water",
}

PREPARATION_WORDS = {
    "fresh",
    "chopped",
    "diced",
    "sliced",
    "minced",
    "cooked",
    "raw",
    "large",
    "small",
    "medium",
    "optional",
    "finely",
    "roughly",
    "thinly",
    "divided",
    "drained",
    "rinsed",
    "peeled",
    "crushed",
    "ground",
    "grated",
}

UNIT_WORDS = {
    "cup",
    "cups",
    "teaspoon",
    "teaspoons",
    "tsp",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "ounce",
    "ounces",
    "oz",
    "pound",
    "pounds",
    "lb",
    "lbs",
    "gram",
    "grams",
    "g",
    "kg",
    "ml",
    "liter",
    "liters",
    "pinch",
    "dash",
    "can",
    "cans",
    "package",
    "packages",
    "slice",
    "slices",
}

SPICE_TERMS = {
    "salt",
    "pepper",
    "cumin",
    "paprika",
    "oregano",
    "basil",
    "thyme",
    "rosemary",
    "parsley",
    "cilantro",
    "cinnamon",
    "nutmeg",
    "ginger",
    "turmeric",
    "seasoning",
    "spice",
    "herb",
}

OIL_FAT_TERMS = {"oil", "butter", "ghee", "lard", "shortening", "margarine"}
SAUCE_TERMS = {"sauce", "ketchup", "mustard", "mayo", "mayonnaise", "dressing", "vinegar", "salsa"}
PROTEIN_TERMS = {
    "chicken",
    "beef",
    "pork",
    "turkey",
    "lamb",
    "fish",
    "salmon",
    "tuna",
    "shrimp",
    "tofu",
    "tempeh",
    "egg",
    "eggs",
    "lentil",
    "lentils",
    "bean",
    "beans",
}
CARB_TERMS = {"rice", "pasta", "noodle", "noodles", "oats", "oat", "potato", "bread", "flour", "tortilla"}
FRUIT_VEG_TERMS = {
    "apple",
    "banana",
    "berry",
    "berries",
    "tomato",
    "onion",
    "garlic",
    "spinach",
    "lettuce",
    "carrot",
    "broccoli",
    "pepper",
    "zucchini",
    "avocado",
    "vegetable",
    "fruit",
}
DAIRY_LIQUID_TERMS = {"milk", "yogurt", "cream", "buttermilk", "kefir"}

ALLERGEN_LEXICONS = {
    "contains_dairy": {"milk", "cheese", "yogurt", "cream", "butter", "whey", "casein", "dairy"},
    "contains_egg": {"egg", "eggs", "omelet", "omelette", "mayonnaise"},
    "contains_peanut": {"peanut", "peanuts", "groundnut"},
    "contains_tree_nuts": {
        "almond",
        "almonds",
        "walnut",
        "walnuts",
        "cashew",
        "cashews",
        "pecan",
        "pecans",
        "pistachio",
        "hazelnut",
        "macadamia",
        "pine nut",
    },
    "contains_shellfish": {"shrimp", "crab", "lobster", "clam", "oyster", "mussel", "scallop", "shellfish"},
    "contains_fish": {"fish", "salmon", "tuna", "cod", "halibut", "anchovy", "anchovies", "sardine", "trout"},
    "contains_gluten": {"wheat", "barley", "rye", "flour", "pasta", "bread", "noodle", "noodles", "cracker"},
    "contains_soy": {"soy", "soya", "tofu", "tempeh", "edamame", "miso"},
    "contains_sesame": {"sesame", "tahini"},
    "contains_pork": {"pork", "bacon", "ham", "prosciutto", "sausage", "lard", "pepperoni"},
    "contains_alcohol": {"wine", "beer", "vodka", "rum", "whiskey", "bourbon", "brandy", "liqueur", "alcohol"},
}

MEAT_TERMS = {
    "beef",
    "pork",
    "chicken",
    "turkey",
    "lamb",
    "bacon",
    "ham",
    "sausage",
    "prosciutto",
    "pepperoni",
    "duck",
    "bison",
    "veal",
}
HONEY_TERMS = {"honey"}
GLUTEN_FREE_HINTS = {"gluten free", "gluten-free"}


@dataclass
class FoodChoice:
    item: FoodItem
    method: str
    score: float
    matched_term: str


@dataclass
class MatchedIngredient:
    original_label: str
    normalized_name: str
    food_item: FoodItem
    grams: float
    method: str
    score: float


@dataclass
class CandidateRecipe:
    row_number: int
    title: str
    slug: str
    directions: str
    source: str | None
    link: str | None
    category: str
    meal_slot: str
    primary_diet_type: str
    diet_tags: dict[str, bool]
    allergen_flags: dict[str, bool]
    matched_ingredients: list[MatchedIngredient]
    unmatched_ingredients: list[str]
    match_ratio: float
    totals: dict[str, float]
    quality_score: float
    buckets: set[str]


class RecipeNLGImporter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.report: dict[str, Any] = {
            "rows_scanned": 0,
            "recipes_considered": 0,
            "recipes_imported": 0,
            "recipes_skipped": 0,
            "match_ratios": [],
            "skip_reasons": Counter(),
            "bucket_counts": Counter(),
            "slot_counts": Counter(),
            "slot_quota_targets": self._slot_targets(),
            "allergen_flag_counts": Counter(),
            "diet_tag_counts": Counter(),
            "top_unmatched_ingredients": Counter(),
            "rejected_dessert_junk_recipes": 0,
            "rejected_calorie_range": 0,
            "ignored_minor_unmatched_ingredients": Counter(),
            "imported_examples": [],
            "accepted_examples_by_slot": defaultdict(list),
            "skipped_examples": [],
            "suspicious_high_protein_rejects": [],
        }
        self.food_by_name: dict[str, FoodItem] = {}
        self.food_by_normalized_name: dict[str, FoodItem] = {}
        self.food_by_alias: dict[str, FoodItem] = {}
        self.fuzzy_choices: list[str] = []
        self.fuzzy_choice_map: dict[str, tuple[FoodItem, str]] = {}

    def _slot_targets(self) -> dict[str, int]:
        return {
            "breakfast": int(self.args.target_breakfast_count),
            "lunch": int(self.args.target_lunch_count),
            "dinner": int(self.args.target_dinner_count),
            "snack": int(self.args.target_snack_count),
        }

    def run(self) -> None:
        file_path = Path(self.args.file)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"RecipeNLG file not found: {file_path}")

        with SessionLocal() as db:
            self._validate_schema(db)
            self._load_food_index(db)
            self._scan_csv(db, file_path)
            if not self.args.dry_run:
                db.commit()

        self._write_report(file_path)
        print(
            "RecipeNLG import complete. "
            f"scanned={self.report['rows_scanned']} "
            f"imported={self.report['recipes_imported']} "
            f"skipped={self.report['recipes_skipped']} "
            f"dry_run={self.args.dry_run}"
        )

    def _validate_schema(self, db: Session) -> None:
        inspector = inspect(db.bind)
        required = {
            "recipes": {"diet_tags_json", "allergen_flags_json"},
            "meal_templates": {"diet_tags_json", "allergen_flags_json"},
        }
        missing: list[str] = []
        for table_name, columns in required.items():
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            missing.extend(f"{table_name}.{column}" for column in columns - existing)

        if missing:
            message = (
                "Missing RecipeNLG classification columns: "
                + ", ".join(sorted(missing))
                + ". Run Alembic upgrade head before importing."
            )
            if self.args.strict or not self.args.dry_run:
                raise RuntimeError(message)
            print(f"WARNING: {message}")

    def _load_food_index(self, db: Session) -> None:
        foods = list(
            db.scalars(
                select(FoodItem)
                .options(selectinload(FoodItem.nutrition_fact), selectinload(FoodItem.aliases))
                .where(FoodItem.is_active.is_(True))
            ).all()
        )

        for food in foods:
            if food.nutrition_fact is None:
                continue

            name = normalize_text(food.name)
            normalized_name = normalize_text(food.normalized_name)
            if name:
                self.food_by_name.setdefault(name, food)
                self._add_fuzzy_choice(name, food, "food_name")
            if normalized_name:
                self.food_by_normalized_name.setdefault(normalized_name, food)
                self._add_fuzzy_choice(normalized_name, food, "normalized_name")

            for alias in food.aliases or []:
                alias_term = normalize_text(alias.normalized_alias or alias.alias_text)
                if alias_term:
                    self.food_by_alias.setdefault(alias_term, food)
                    self._add_fuzzy_choice(alias_term, food, "alias")

    def _add_fuzzy_choice(self, term: str, food: FoodItem, source: str) -> None:
        if term in self.fuzzy_choice_map:
            return
        self.fuzzy_choice_map[term] = (food, source)
        self.fuzzy_choices.append(term)

    def _scan_csv(self, db: Session, file_path: Path) -> None:
        selected_count = 0
        bucket_quota = max(1, self.args.target_count // len(SCENARIO_BUCKETS))
        chunks = pd.read_csv(file_path, chunksize=1000)

        for chunk in chunks:
            columns = {column.lower(): column for column in chunk.columns}
            self._validate_columns(columns)

            chunk_candidates: list[CandidateRecipe] = []
            for _, row in chunk.iterrows():
                if self.args.scan_limit and self.report["rows_scanned"] >= self.args.scan_limit:
                    break
                self.report["rows_scanned"] += 1

                candidate = self._build_candidate(row, columns, self.report["rows_scanned"])
                if candidate is None:
                    continue
                chunk_candidates.append(candidate)

            for candidate in sorted(chunk_candidates, key=self._candidate_selection_key, reverse=True):
                if self._selection_complete(selected_count):
                    break

                if not self._can_accept_candidate(candidate, selected_count, bucket_quota):
                    self._skip(candidate.title, "bucket temporarily saturated")
                    continue

                if self._create_or_update_recipe(db, candidate):
                    selected_count += 1
                    self._record_import(candidate)

            if self._selection_complete(selected_count):
                break
            if self.args.scan_limit and self.report["rows_scanned"] >= self.args.scan_limit:
                break

    def _validate_columns(self, columns: dict[str, str]) -> None:
        required = {"title"}
        missing = sorted(required - set(columns))
        if missing and self.args.strict:
            raise RuntimeError(f"Missing required RecipeNLG columns: {', '.join(missing)}")

    def _build_candidate(
        self,
        row: Any,
        columns: dict[str, str],
        row_number: int,
    ) -> CandidateRecipe | None:
        title = clean_cell(row.get(columns.get("title", ""), ""))
        source = clean_cell(row.get(columns.get("source", ""), "")) or None
        link = clean_cell(row.get(columns.get("link", ""), "")) or None

        if self.args.source_filter and self.args.source_filter.lower() not in {"all", "any", "none"}:
            if normalize_text(source) != normalize_text(self.args.source_filter):
                self._skip(title or f"row {row_number}", "source filter mismatch")
                return None

        if not is_reasonable_title(title):
            self._skip(title or f"row {row_number}", "spam or unclear title")
            return None

        dessert_like = is_dessert_title(title)
        low_quality_meal = is_low_quality_meal_title(title)
        healthy_snack_title = is_healthy_snack_text(title)
        if (dessert_like and not self.args.allow_dessert_snacks) or (
            low_quality_meal and not healthy_snack_title
        ):
            self.report["rejected_dessert_junk_recipes"] += 1
            self._skip(title, "dessert or junk title")
            return None

        directions = parse_directions(clean_cell(row.get(columns.get("directions", ""), "")))
        if len(directions) < 40:
            self._skip(title, "missing or unclear directions")
            return None

        ingredients_raw = parse_list_cell(row.get(columns.get("ingredients", ""), ""))
        ner_raw = parse_list_cell(row.get(columns.get("ner", ""), ""))
        ingredient_terms = ner_raw if ner_raw else ingredients_raw
        ingredient_terms = [normalize_ingredient(term) for term in ingredient_terms if normalize_ingredient(term)]

        if not (self.args.min_ingredients <= len(ingredient_terms) <= self.args.max_ingredients):
            self._skip(title, "ingredient count outside limits")
            return None

        self.report["recipes_considered"] += 1
        matched, unmatched, ignored_minor = self._match_ingredients(ingredient_terms, ingredients_raw)
        for ingredient in ignored_minor:
            self.report["ignored_minor_unmatched_ingredients"][ingredient] += 1
        hard_ingredient_count = max(1, len(ingredient_terms) - len(ignored_minor))
        match_ratio = len(matched) / hard_ingredient_count
        if match_ratio < self.args.min_match_ratio:
            for ingredient in unmatched:
                self.report["top_unmatched_ingredients"][ingredient] += 1
            self._skip(title, "low ingredient match ratio")
            return None

        totals = calculate_totals(matched)
        if totals["calories"] <= 0:
            self._skip(title, "no calculable nutrition")
            return None

        text_for_classification = " ".join(
            [title, directions, *ingredient_terms, *(item.food_item.name for item in matched)]
        )
        allergen_flags = classify_allergens(text_for_classification)
        raw_high_protein = is_high_protein(
            totals,
            self.args.min_protein_for_high_protein,
            self.args.min_protein_calorie_ratio_for_high_protein,
        )
        if dessert_like and raw_high_protein:
            self._record_suspicious_high_protein_reject(title, totals)

        diet_tags = classify_diet_tags(
            text_for_classification,
            totals,
            allergen_flags,
            min_protein_g=self.args.min_protein_for_high_protein,
            min_protein_calorie_ratio=self.args.min_protein_calorie_ratio_for_high_protein,
            dessert_like=dessert_like,
        )
        category = infer_category(title, ingredient_terms)
        meal_slot = infer_meal_slot(title, ingredient_terms, category, dessert_like=dessert_like)
        if dessert_like and self.args.exclude_desserts_from_meals:
            meal_slot = "snack"
            category = "snack"

        if not self._is_calorie_range_valid(meal_slot, totals["calories"]):
            self.report["rejected_calorie_range"] += 1
            self._skip(title, "slot calorie range failed")
            return None

        primary_diet_type = choose_primary_diet_type(diet_tags)
        buckets = scenario_buckets(diet_tags, meal_slot)

        quality_score = score_candidate(
            match_ratio=match_ratio,
            matched_count=len(matched),
            totals=totals,
            directions=directions,
            title=title,
        )
        slug = stable_recipe_slug(title=title, link=link, row_number=row_number)

        return CandidateRecipe(
            row_number=row_number,
            title=title,
            slug=slug,
            directions=directions,
            source=source,
            link=link,
            category=category,
            meal_slot=meal_slot,
            primary_diet_type=primary_diet_type,
            diet_tags=diet_tags,
            allergen_flags=allergen_flags,
            matched_ingredients=matched,
            unmatched_ingredients=unmatched,
            match_ratio=match_ratio,
            totals=totals,
            quality_score=quality_score,
            buckets=buckets,
        )

    def _match_ingredients(
        self,
        ingredient_terms: list[str],
        original_ingredients: list[str],
    ) -> tuple[list[MatchedIngredient], list[str], list[str]]:
        matched: list[MatchedIngredient] = []
        unmatched: list[str] = []
        ignored_minor: list[str] = []
        seen_food_ids: set[str] = set()

        for index, ingredient in enumerate(ingredient_terms):
            choice = self._match_one_ingredient(ingredient)
            if choice is None:
                if is_minor_unmatched_ingredient(ingredient):
                    ignored_minor.append(ingredient)
                    continue
                unmatched.append(ingredient)
                continue

            original_label = original_ingredients[index] if index < len(original_ingredients) else ingredient
            grams = estimate_grams(ingredient, choice.item.name)
            matched.append(
                MatchedIngredient(
                    original_label=str(original_label),
                    normalized_name=ingredient,
                    food_item=choice.item,
                    grams=grams,
                    method=choice.method,
                    score=choice.score,
                )
            )
            seen_food_ids.add(choice.item.id)

        if len(seen_food_ids) < max(2, min(3, len(matched))):
            unmatched.append("too few distinct matched food items")

        return matched, unmatched, ignored_minor

    def _match_one_ingredient(self, ingredient: str) -> FoodChoice | None:
        if ingredient in self.food_by_name:
            return FoodChoice(self.food_by_name[ingredient], "exact_food_name", 100.0, ingredient)
        if ingredient in self.food_by_normalized_name:
            return FoodChoice(
                self.food_by_normalized_name[ingredient],
                "exact_normalized_name",
                100.0,
                ingredient,
            )
        if ingredient in self.food_by_alias:
            return FoodChoice(self.food_by_alias[ingredient], "exact_alias", 100.0, ingredient)

        if not self.fuzzy_choices:
            return None
        fuzzy = process.extractOne(
            ingredient,
            self.fuzzy_choices,
            scorer=fuzz.token_set_ratio,
            score_cutoff=self.args.fuzzy_threshold,
        )
        if fuzzy is None:
            return None

        matched_term, score, _ = fuzzy
        food, source = self.fuzzy_choice_map[matched_term]
        return FoodChoice(food, f"fuzzy_{source}", float(score), matched_term)

    def _passes_bucket_balance(
        self,
        candidate: CandidateRecipe,
        selected_count: int,
        bucket_quota: int,
    ) -> bool:
        if selected_count < max(10, self.args.target_count // 10):
            return True
        if any(self.report["bucket_counts"][bucket] < bucket_quota for bucket in candidate.buckets):
            return True
        if all(self.report["bucket_counts"][bucket] >= bucket_quota for bucket in SCENARIO_BUCKETS):
            return True
        return candidate.quality_score >= 2.8

    def _candidate_selection_key(self, candidate: CandidateRecipe) -> tuple[int, int, float]:
        slot_targets = self.report["slot_quota_targets"]
        slot_count = self.report["slot_counts"][candidate.meal_slot]
        slot_deficit = max(0, slot_targets.get(candidate.meal_slot, 0) - slot_count)
        return (
            1 if slot_deficit > 0 else 0,
            slot_title_confidence(candidate.meal_slot, candidate.title),
            candidate.quality_score,
        )

    def _can_accept_candidate(
        self,
        candidate: CandidateRecipe,
        selected_count: int,
        bucket_quota: int,
    ) -> bool:
        if selected_count >= self.args.target_count:
            return False

        slot_targets = self.report["slot_quota_targets"]
        slot_count = self.report["slot_counts"][candidate.meal_slot]
        slot_target = slot_targets.get(candidate.meal_slot, 0)
        slot_needs_candidates = slot_count < slot_target

        if not slot_needs_candidates and not self._slot_quota_coverage_reached():
            return False

        return self._passes_bucket_balance(candidate, selected_count, bucket_quota)

    def _slot_quota_coverage_reached(self) -> bool:
        slot_targets = self.report["slot_quota_targets"]
        return all(self.report["slot_counts"][slot] >= slot_targets.get(slot, 0) for slot in SLOT_ORDER)

    def _selection_complete(self, selected_count: int) -> bool:
        return selected_count >= self.args.target_count and self._slot_quota_coverage_reached()

    def _is_calorie_range_valid(self, meal_slot: str, calories: float) -> bool:
        min_calories, max_calories = slot_calorie_range(meal_slot)
        return min_calories <= calories <= max_calories

    def _record_suspicious_high_protein_reject(
        self,
        title: str,
        totals: dict[str, float],
    ) -> None:
        if len(self.report["suspicious_high_protein_rejects"]) >= 15:
            return
        protein_ratio = (totals["protein_g"] * 4 / totals["calories"]) if totals["calories"] > 0 else 0
        self.report["suspicious_high_protein_rejects"].append(
            {
                "title": title,
                "calories": totals["calories"],
                "protein_g": totals["protein_g"],
                "protein_calorie_ratio": round(protein_ratio, 3),
            }
        )

    def _create_or_update_recipe(self, db: Session, candidate: CandidateRecipe) -> bool:
        existing = db.scalar(select(Recipe).where(Recipe.slug == candidate.slug))
        if existing and existing.source != SOURCE_CODE:
            self._skip(candidate.title, "slug collides with non-RecipeNLG recipe")
            return False
        if existing and not self.args.force:
            self._skip(candidate.title, "duplicate RecipeNLG recipe")
            return False

        if self.args.dry_run:
            return True

        recipe = existing or Recipe(slug=candidate.slug)
        recipe.name = candidate.title[:255]
        recipe.description = build_description(candidate)
        recipe.instructions = candidate.directions
        recipe.servings = 1
        recipe.category = candidate.category
        recipe.diet_type = candidate.primary_diet_type
        recipe.diet_tags_json = candidate.diet_tags
        recipe.allergen_flags_json = candidate.allergen_flags
        recipe.source = SOURCE_CODE
        recipe.is_active = True
        recipe.total_calories = candidate.totals["calories"]
        recipe.total_protein_g = candidate.totals["protein_g"]
        recipe.total_carbs_g = candidate.totals["carbs_g"]
        recipe.total_fat_g = candidate.totals["fat_g"]
        db.add(recipe)
        db.flush()

        if existing:
            for ingredient in list(existing.ingredients):
                db.delete(ingredient)
            db.flush()

        for position, ingredient in enumerate(candidate.matched_ingredients, start=1):
            db.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    food_item_id=ingredient.food_item.id,
                    position=position,
                    ingredient_name_snapshot=ingredient.food_item.name,
                    quantity_label=ingredient.original_label[:100],
                    grams=ingredient.grams,
                    notes=(
                        f"RecipeNLG original='{ingredient.original_label[:120]}'; "
                        f"normalized='{ingredient.normalized_name}'; "
                        f"match_method={ingredient.method}; score={ingredient.score:.1f}"
                    ),
                )
            )

        self._create_or_update_template(db, recipe, candidate)
        return True

    def _create_or_update_template(
        self,
        db: Session,
        recipe: Recipe,
        candidate: CandidateRecipe,
    ) -> None:
        template_slug = f"{candidate.slug}-template"
        template = db.scalar(
            select(MealTemplate).where(
                MealTemplate.slug == template_slug,
                MealTemplate.source == SOURCE_CODE,
            )
        )
        if template is None:
            template = MealTemplate(slug=template_slug)

        template.recipe_id = recipe.id
        template.name = candidate.title[:255]
        template.meal_slot = candidate.meal_slot
        template.category = candidate.category
        template.diet_type = candidate.primary_diet_type
        template.diet_tags_json = candidate.diet_tags
        template.allergen_flags_json = candidate.allergen_flags
        template.source = SOURCE_CODE
        template.description = build_description(candidate)
        template.notes = "One template per RecipeNLG recipe. Thesis/demo use only."
        template.estimated_calories = candidate.totals["calories"]
        template.estimated_protein_g = candidate.totals["protein_g"]
        template.estimated_carbs_g = candidate.totals["carbs_g"]
        template.estimated_fat_g = candidate.totals["fat_g"]
        template.is_active = True
        db.add(template)

    def _record_import(self, candidate: CandidateRecipe) -> None:
        self.report["recipes_imported"] += 1
        self.report["match_ratios"].append(candidate.match_ratio)
        self.report["slot_counts"][candidate.meal_slot] += 1
        for bucket in candidate.buckets:
            self.report["bucket_counts"][bucket] += 1
        for flag, enabled in candidate.allergen_flags.items():
            if enabled:
                self.report["allergen_flag_counts"][flag] += 1
        for tag, enabled in candidate.diet_tags.items():
            if enabled:
                self.report["diet_tag_counts"][tag] += 1
        if len(self.report["imported_examples"]) < 10:
            self.report["imported_examples"].append(
                {
                    "title": candidate.title,
                    "match_ratio": round(candidate.match_ratio, 3),
                    "meal_slot": candidate.meal_slot,
                    "calories": candidate.totals["calories"],
                    "protein_g": candidate.totals["protein_g"],
                    "carbs_g": candidate.totals["carbs_g"],
                    "fat_g": candidate.totals["fat_g"],
                    "buckets": sorted(candidate.buckets),
                }
            )
        slot_examples = self.report["accepted_examples_by_slot"][candidate.meal_slot]
        if len(slot_examples) < 5:
            slot_examples.append(
                {
                    "title": candidate.title,
                    "match_ratio": round(candidate.match_ratio, 3),
                    "calories": candidate.totals["calories"],
                    "protein_g": candidate.totals["protein_g"],
                    "carbs_g": candidate.totals["carbs_g"],
                    "fat_g": candidate.totals["fat_g"],
                }
            )

    def _skip(self, title: str, reason: str) -> None:
        self.report["recipes_skipped"] += 1
        self.report["skip_reasons"][reason] += 1
        if len(self.report["skipped_examples"]) < 10:
            self.report["skipped_examples"].append({"title": title[:120], "reason": reason})

    def _write_report(self, file_path: Path) -> None:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        imported = int(self.report["recipes_imported"])
        average_match_ratio = (
            sum(self.report["match_ratios"]) / len(self.report["match_ratios"])
            if self.report["match_ratios"]
            else 0
        )

        lines = [
            "# RecipeNLG Import Report",
            "",
            "RecipeNLG-derived data is thesis/demo-only and must be removed or replaced before commercialization.",
            "",
            "## Run configuration",
            "",
            f"- File: `{file_path}`",
            f"- Dry run: `{self.args.dry_run}`",
            f"- Target count: `{self.args.target_count}`",
            f"- Target breakfast count: `{self.args.target_breakfast_count}`",
            f"- Target lunch count: `{self.args.target_lunch_count}`",
            f"- Target dinner count: `{self.args.target_dinner_count}`",
            f"- Target snack count: `{self.args.target_snack_count}`",
            f"- Scan limit: `{self.args.scan_limit}`",
            f"- Source filter: `{self.args.source_filter}`",
            f"- Min match ratio: `{self.args.min_match_ratio}`",
            f"- Fuzzy threshold: `{self.args.fuzzy_threshold}`",
            f"- Exclude desserts from meals: `{self.args.exclude_desserts_from_meals}`",
            f"- Allow dessert snacks: `{self.args.allow_dessert_snacks}`",
            f"- Slot calorie ranges: `{slot_calorie_ranges_label()}`",
            f"- High protein thresholds: `{self.args.min_protein_for_high_protein}g` and `{self.args.min_protein_calorie_ratio_for_high_protein}` protein-calorie ratio",
            f"- Strict: `{self.args.strict}`",
            f"- Force updates: `{self.args.force}`",
            "",
            "## Summary",
            "",
            f"- Rows scanned: {self.report['rows_scanned']}",
            f"- Recipes considered: {self.report['recipes_considered']}",
            f"- Recipes imported: {imported}",
            f"- Recipes skipped: {self.report['recipes_skipped']}",
            f"- Average match ratio: {average_match_ratio:.3f}",
            "",
            "## Slot quota results",
            "",
            slot_quota_table(self.report["slot_quota_targets"], self.report["slot_counts"]),
            "",
            "## Slot quota examples",
            "",
            slot_examples_sections(self.report["accepted_examples_by_slot"]),
            "",
            "## Quality-control rejects",
            "",
            f"- Rejected dessert/junk recipes: {self.report['rejected_dessert_junk_recipes']}",
            f"- Rejected calorie range recipes: {self.report['rejected_calorie_range']}",
            f"- Ignored minor unmatched ingredients: {sum(self.report['ignored_minor_unmatched_ingredients'].values())}",
            "",
            "## Bucket counts",
            "",
            counter_table(self.report["bucket_counts"], SCENARIO_BUCKETS),
            "",
            "## Allergen flag counts",
            "",
            counter_table(self.report["allergen_flag_counts"], sorted(ALLERGEN_LEXICONS)),
            "",
            "## Diet tag counts",
            "",
            counter_table(self.report["diet_tag_counts"], sorted(DIET_TAG_NAMES)),
            "",
            "## Skip reasons",
            "",
            counter_table(self.report["skip_reasons"]),
            "",
            "## Top unmatched ingredients",
            "",
            counter_table(self.report["top_unmatched_ingredients"], limit=30),
            "",
            "## Ignored minor unmatched ingredients",
            "",
            counter_table(self.report["ignored_minor_unmatched_ingredients"], limit=30),
            "",
            "## Suspicious high-protein rejects",
            "",
            examples_table(self.report["suspicious_high_protein_rejects"]),
            "",
            "## Accepted examples by slot",
            "",
            slot_examples_sections(self.report["accepted_examples_by_slot"]),
            "",
            "## Examples of imported recipes",
            "",
            examples_table(self.report["imported_examples"]),
            "",
            "## Examples of skipped recipes",
            "",
            examples_table(self.report["skipped_examples"]),
            "",
            "## Notes",
            "",
            "- Importer only matches ingredients to existing active `FoodItem` rows.",
            "- Importer does not create `FoodItem`, `NutritionFact`, `food_logs`, meal logs, users, or meal plans.",
            "- Nutrition totals are estimated from matched `NutritionFact` macros and conservative gram defaults.",
            "- Allergen and diet classifications are ingredient-based heuristic flags, not medical certification.",
        ]
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def clean_cell(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def parse_list_cell(value: Any) -> list[str]:
    text = clean_cell(value)
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        if isinstance(parsed, tuple):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (SyntaxError, ValueError):
        pass
    return [part.strip() for part in re.split(r"\s*\|\s*|\n|;", text) if part.strip()]


def parse_directions(value: str) -> str:
    parsed = parse_list_cell(value)
    if parsed:
        return " ".join(parsed)
    return value


def normalize_text(value: str | None) -> str:
    text = (value or "").lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_ingredient(value: str | None) -> str:
    text = normalize_text(value)
    text = re.sub(r"\b\d+([./]\d+)?\b", " ", text)
    words = [
        word
        for word in text.split()
        if word not in PREPARATION_WORDS and word not in UNIT_WORDS
    ]
    return re.sub(r"\s+", " ", " ".join(words)).strip()


def is_reasonable_title(title: str) -> bool:
    normalized = normalize_text(title)
    if len(normalized) < 3 or len(title) > 180:
        return False
    if "http" in normalized or "www" in normalized:
        return False
    if normalized in {"untitled", "recipe", "test", "none", "unknown"}:
        return False
    return bool(re.search(r"[a-z]", normalized))


def is_dessert_title(title: str) -> bool:
    return contains_any(title, DESSERT_TITLE_TERMS)


def is_low_quality_meal_title(title: str) -> bool:
    return contains_any(title, LOW_QUALITY_MEAL_TITLE_TERMS)


def is_healthy_snack_text(text: str) -> bool:
    return contains_any(text, HEALTHY_SNACK_TERMS)


def is_breakfast_candidate(title: str, ingredients: list[str]) -> bool:
    if contains_any(title, BREAKFAST_TERMS):
        return True
    if contains_any(title, SAVORY_NON_BREAKFAST_TITLE_TERMS):
        return False
    return contains_any(" ".join(ingredients), BREAKFAST_INGREDIENT_TERMS)


def is_minor_unmatched_ingredient(ingredient: str) -> bool:
    normalized = normalize_text(ingredient)
    return normalized in MINOR_UNMATCHED_INGREDIENTS


def contains_any(text: str, terms: Iterable[str]) -> bool:
    normalized = normalize_text(text)
    return any(re.search(rf"\b{re.escape(term)}s?\b", normalized) for term in terms)


def estimate_grams(ingredient: str, matched_food_name: str) -> float:
    text = f"{ingredient} {matched_food_name}".lower()
    if contains_any(text, OIL_FAT_TERMS):
        return 10.0
    if contains_any(text, SPICE_TERMS):
        return 2.0
    if contains_any(text, SAUCE_TERMS):
        return 15.0
    if contains_any(text, {"egg", "eggs"}):
        return 50.0
    if contains_any(text, DAIRY_LIQUID_TERMS):
        return 150.0
    if contains_any(text, PROTEIN_TERMS):
        return 150.0
    if contains_any(text, CARB_TERMS):
        return 150.0
    if contains_any(text, FRUIT_VEG_TERMS):
        return 80.0
    return 50.0


def calculate_totals(matched: list[MatchedIngredient]) -> dict[str, float]:
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for ingredient in matched:
        nutrition = ingredient.food_item.nutrition_fact
        if nutrition is None:
            continue
        factor = ingredient.grams / 100.0
        totals["calories"] += float(nutrition.calories_per_100g) * factor
        totals["protein_g"] += float(nutrition.protein_g_per_100g) * factor
        totals["carbs_g"] += float(nutrition.carbs_g_per_100g) * factor
        totals["fat_g"] += float(nutrition.fat_g_per_100g) * factor
    return {key: round(value, 2) for key, value in totals.items()}


def classify_allergens(text: str) -> dict[str, bool]:
    normalized = normalize_text(text)
    return {flag: contains_any(normalized, terms) for flag, terms in ALLERGEN_LEXICONS.items()}


DIET_TAG_NAMES = {
    "vegetarian_candidate",
    "vegan_candidate",
    "halal_candidate",
    "kosher_candidate",
    "gluten_free_candidate",
    "dairy_free_candidate",
    "egg_free_candidate",
    "peanut_free_candidate",
    "nut_free_candidate",
    "high_protein",
    "low_carb",
    "balanced",
}


def classify_diet_tags(
    text: str,
    totals: dict[str, float],
    allergen_flags: dict[str, bool],
    min_protein_g: float,
    min_protein_calorie_ratio: float,
    dessert_like: bool = False,
) -> dict[str, bool]:
    normalized = normalize_text(text)
    contains_meat = contains_any(normalized, MEAT_TERMS)
    contains_fish_or_shellfish = allergen_flags["contains_fish"] or allergen_flags["contains_shellfish"]
    vegetarian = not contains_meat and not contains_fish_or_shellfish
    vegan = vegetarian and not (
        allergen_flags["contains_dairy"]
        or allergen_flags["contains_egg"]
        or contains_any(normalized, HONEY_TERMS)
    )
    gluten_free = (
        not allergen_flags["contains_gluten"]
        or contains_any(normalized, GLUTEN_FREE_HINTS)
    )
    calories = totals["calories"]
    protein = totals["protein_g"]
    carbs = totals["carbs_g"]
    fat = totals["fat_g"]
    protein_calorie_ratio = (protein * 4 / calories) if calories > 0 else 0
    carb_calorie_ratio = (carbs * 4 / calories) if calories > 0 else 0
    fat_calorie_ratio = (fat * 9 / calories) if calories > 0 else 0

    return {
        "vegetarian_candidate": vegetarian,
        "vegan_candidate": vegan,
        "halal_candidate": not allergen_flags["contains_pork"] and not allergen_flags["contains_alcohol"],
        "kosher_candidate": not allergen_flags["contains_pork"] and not allergen_flags["contains_shellfish"],
        "gluten_free_candidate": gluten_free,
        "dairy_free_candidate": not allergen_flags["contains_dairy"],
        "egg_free_candidate": not allergen_flags["contains_egg"],
        "peanut_free_candidate": not allergen_flags["contains_peanut"],
        "nut_free_candidate": not allergen_flags["contains_peanut"] and not allergen_flags["contains_tree_nuts"],
        "high_protein": (
            not dessert_like
            and is_high_protein(totals, min_protein_g, min_protein_calorie_ratio)
        ),
        "low_carb": carbs <= 30,
        "balanced": (
            300 <= calories <= 800
            and 0.10 <= protein_calorie_ratio <= 0.40
            and 0.20 <= carb_calorie_ratio <= 0.65
            and 0.15 <= fat_calorie_ratio <= 0.45
        ),
    }


def is_high_protein(
    totals: dict[str, float],
    min_protein_g: float,
    min_protein_calorie_ratio: float,
) -> bool:
    calories = totals["calories"]
    if calories <= 0:
        return False
    protein = totals["protein_g"]
    protein_calorie_ratio = protein * 4 / calories
    return protein >= min_protein_g and protein_calorie_ratio >= min_protein_calorie_ratio


def choose_primary_diet_type(diet_tags: dict[str, bool]) -> str:
    for tag in (
        "vegan_candidate",
        "vegetarian_candidate",
        "high_protein",
        "low_carb",
        "gluten_free_candidate",
        "balanced",
        "halal_candidate",
    ):
        if diet_tags.get(tag):
            return tag
    return "general"


def infer_category(title: str, ingredients: list[str]) -> str:
    text = normalize_text(" ".join([title, *ingredients]))
    if is_healthy_snack_text(title):
        return "snack"
    if is_breakfast_candidate(title, ingredients):
        return "breakfast"
    if contains_any(text, {"dessert", "cookie", "cake", "pie", "brownie", "snack"}):
        return "snack"
    if contains_any(text, {"soup", "stew", "chili"}):
        return "soup"
    if contains_any(text, {"pasta", "casserole", "roast", "dinner"}):
        return "dinner"
    if contains_any(text, {"salad", "bowl", "sandwich"}):
        return "lunch"
    return "recipe"


def infer_meal_slot(
    title: str,
    ingredients: list[str],
    category: str,
    dessert_like: bool = False,
) -> str:
    if dessert_like:
        return "snack"
    text = normalize_text(" ".join([title, *ingredients]))
    if is_healthy_snack_text(title):
        return "snack"
    if category == "breakfast":
        return "breakfast"
    if is_breakfast_candidate(title, ingredients):
        return "breakfast"
    if category == "snack" or contains_any(text, {"dessert", "snack", "cookie", "cake", "pie", "smoothie"}):
        return "snack"
    if contains_any(text, {"roast", "stew", "casserole", "pasta dinner", "dinner"}):
        return "dinner"
    return "lunch"


def scenario_buckets(diet_tags: dict[str, bool], meal_slot: str) -> set[str]:
    buckets = {meal_slot}
    if diet_tags.get("balanced"):
        buckets.add("general_balanced")
    for tag in DIET_TAG_NAMES:
        if diet_tags.get(tag):
            buckets.add(tag)
    return buckets


def score_candidate(
    match_ratio: float,
    matched_count: int,
    totals: dict[str, float],
    directions: str,
    title: str,
) -> float:
    score = match_ratio * 4.0
    if 250 <= totals["calories"] <= 900:
        score += 1.5
    if 3 <= matched_count <= 10:
        score += 1.0
    if len(directions) >= 120:
        score += 0.5
    if is_reasonable_title(title):
        score += 0.5
    return score


def slot_title_confidence(meal_slot: str, title: str) -> int:
    if meal_slot == "breakfast":
        return 1 if contains_any(title, BREAKFAST_TERMS) else 0
    if meal_slot == "snack":
        return 1 if is_healthy_snack_text(title) else 0
    if meal_slot == "dinner":
        return 1 if contains_any(title, {"dinner", "roast", "stew", "casserole"}) else 0
    if meal_slot == "lunch":
        return 1 if contains_any(title, {"lunch", "salad", "bowl", "sandwich"}) else 0
    return 0


def stable_recipe_slug(title: str, link: str | None, row_number: int) -> str:
    base = slugify(title)[:70] or "recipenlg-recipe"
    digest = hashlib.sha1(f"{title}|{link or ''}|{row_number}".encode("utf-8")).hexdigest()[:12]
    return f"recipenlg-{digest}-{base}"[:255]


def slugify(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_description(candidate: CandidateRecipe) -> str:
    parts = [DISCLAIMER]
    if candidate.source:
        parts.append(f"RecipeNLG source: {candidate.source}.")
    if candidate.link:
        parts.append(f"Original link: {candidate.link}.")
    parts.append(
        "Allergen and diet tags are heuristic ingredient-based classifications, "
        "not medical or religious certification."
    )
    return " ".join(parts)


def counter_table(counter: Counter, keys: Iterable[str] | None = None, limit: int | None = None) -> str:
    items = [(key, counter.get(key, 0)) for key in keys] if keys else list(counter.most_common(limit))
    if limit is not None and keys is None:
        items = items[:limit]
    if not items:
        return "_None._"
    lines = ["| Item | Count |", "| --- | ---: |"]
    lines.extend(f"| {key} | {value} |" for key, value in items)
    return "\n".join(lines)


def slot_quota_table(targets: dict[str, int], achieved: Counter) -> str:
    lines = ["| Slot | Target | Achieved | Deficit |", "| --- | ---: | ---: | ---: |"]
    for slot in SLOT_ORDER:
        target = targets.get(slot, 0)
        count = achieved.get(slot, 0)
        deficit = max(0, target - count)
        lines.append(f"| {slot} | {target} | {count} | {deficit} |")
    return "\n".join(lines)


def examples_table(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return "_None._"
    keys = sorted({key for example in examples for key in example})
    lines = ["| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    for example in examples:
        values = [str(example.get(key, "")).replace("|", "\\|") for key in keys]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def slot_examples_sections(examples_by_slot: dict[str, list[dict[str, Any]]]) -> str:
    sections: list[str] = []
    for slot in ("breakfast", "lunch", "dinner", "snack"):
        sections.append(f"### {slot.title()}")
        sections.append("")
        sections.append(examples_table(list(examples_by_slot.get(slot, []))))
        sections.append("")
    return "\n".join(sections).strip()


def slot_calorie_range(meal_slot: str) -> tuple[int, int]:
    return SLOT_CALORIE_RANGES.get(meal_slot, SLOT_CALORIE_RANGES["lunch"])


def slot_calorie_ranges_label() -> str:
    return ", ".join(
        f"{slot} {bounds[0]}-{bounds[1]} kcal"
        for slot, bounds in SLOT_CALORIE_RANGES.items()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a high-quality, scenario-balanced RecipeNLG subset.",
    )
    parser.add_argument("--file", default="data/raw/recipenlg/RecipeNLG_dataset.csv")
    parser.add_argument("--target-count", type=int, default=1000)
    parser.add_argument("--target-breakfast-count", type=int, default=150)
    parser.add_argument("--target-lunch-count", type=int, default=350)
    parser.add_argument("--target-dinner-count", type=int, default=350)
    parser.add_argument("--target-snack-count", type=int, default=150)
    parser.add_argument("--scan-limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-match-ratio", type=float, default=0.7)
    parser.add_argument("--fuzzy-threshold", type=int, default=85)
    parser.add_argument("--source-filter", default="Gathered")
    parser.add_argument("--min-ingredients", type=int, default=3)
    parser.add_argument("--max-ingredients", type=int, default=12)
    parser.add_argument(
        "--exclude-desserts-from-meals",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--allow-dessert-snacks", action="store_true", default=False)
    parser.add_argument("--min-meal-calories", type=float, default=250)
    parser.add_argument("--max-meal-calories", type=float, default=900)
    parser.add_argument("--max-snack-calories", type=float, default=400)
    parser.add_argument("--min-protein-for-high-protein", type=float, default=25)
    parser.add_argument(
        "--min-protein-calorie-ratio-for-high-protein",
        type=float,
        default=0.25,
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target_count < 1:
        raise ValueError("--target-count must be at least 1")
    slot_target_total = (
        args.target_breakfast_count
        + args.target_lunch_count
        + args.target_dinner_count
        + args.target_snack_count
    )
    if min(
        args.target_breakfast_count,
        args.target_lunch_count,
        args.target_dinner_count,
        args.target_snack_count,
    ) < 0:
        raise ValueError("slot target counts must be non-negative")
    if slot_target_total > args.target_count:
        raise ValueError("slot target counts must not exceed --target-count")
    if not 0 < args.min_match_ratio <= 1:
        raise ValueError("--min-match-ratio must be in (0, 1]")
    if args.min_ingredients < 1 or args.max_ingredients < args.min_ingredients:
        raise ValueError("ingredient limits are invalid")
    if args.min_meal_calories < 0 or args.max_meal_calories < args.min_meal_calories:
        raise ValueError("meal calorie limits are invalid")
    if args.max_snack_calories < 0:
        raise ValueError("--max-snack-calories must be non-negative")
    if args.min_protein_for_high_protein < 0:
        raise ValueError("--min-protein-for-high-protein must be non-negative")
    if not 0 <= args.min_protein_calorie_ratio_for_high_protein <= 1:
        raise ValueError("--min-protein-calorie-ratio-for-high-protein must be between 0 and 1")
    RecipeNLGImporter(args).run()


if __name__ == "__main__":
    main()
