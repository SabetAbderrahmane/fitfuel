from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.allergy import Allergy
from app.models.dietary_preference import DietaryPreference
from app.models.food_item import FoodItem
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.meal_template import MealTemplate
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.meal_plan import (
    MealPlanCreateRequest,
    MealPlanGenerateRequest,
)


SLOT_CALORIE_SPLITS: dict[str, float] = {
    "breakfast": 0.25,
    "lunch": 0.30,
    "dinner": 0.30,
    "snack": 0.15,
}

VALID_MEAL_SLOTS = set(SLOT_CALORIE_SPLITS)

PLACEHOLDER_NAMES = {
    "",
    "string",
    "test",
    "food",
    "item",
    "sample",
    "unknown",
}

SLOT_RULES: dict[str, dict[str, set[str]]] = {
    "breakfast": {
        "prefer_categories": {"breakfast", "protein", "carb", "dairy", "fruit"},
        "avoid_categories": {"oil", "fat", "condiment", "sauce"},
        "prefer_keywords": {
            "egg",
            "oat",
            "oats",
            "milk",
            "yogurt",
            "banana",
            "toast",
            "bread",
        },
        "avoid_keywords": {"oil", "butter", "rice", "noodle", "pasta"},
    },
    "lunch": {
        "prefer_categories": {"lunch", "protein", "carb", "vegetable"},
        "avoid_categories": {"condiment", "sauce"},
        "prefer_keywords": {
            "chicken",
            "rice",
            "beef",
            "fish",
            "potato",
            "tofu",
            "salad",
        },
        "avoid_keywords": {"oil", "butter"},
    },
    "dinner": {
        "prefer_categories": {"dinner", "protein", "carb", "vegetable"},
        "avoid_categories": {"condiment", "sauce"},
        "prefer_keywords": {
            "chicken",
            "rice",
            "fish",
            "beef",
            "tofu",
            "vegetable",
            "salad",
        },
        "avoid_keywords": {"oil", "butter"},
    },
    "snack": {
        "prefer_categories": {"snack", "protein", "dairy", "fruit"},
        "avoid_categories": {"carb", "oil", "fat", "condiment", "sauce"},
        "prefer_keywords": {
            "egg",
            "yogurt",
            "banana",
            "apple",
            "fruit",
            "nuts",
            "protein",
            "milk",
        },
        "avoid_keywords": {"rice", "pasta", "noodle", "bread", "oil", "butter"},
    },
}

DIET_FORBIDDEN_TERMS: dict[str, set[str]] = {
    "vegetarian": {
        "bacon",
        "beef",
        "chicken",
        "fish",
        "ham",
        "lamb",
        "meat",
        "pork",
        "salmon",
        "sausage",
        "seafood",
        "shrimp",
        "tuna",
        "turkey",
    },
    "vegan": {
        "bacon",
        "beef",
        "butter",
        "cheese",
        "chicken",
        "dairy",
        "egg",
        "fish",
        "ham",
        "honey",
        "lamb",
        "meat",
        "milk",
        "pork",
        "salmon",
        "sausage",
        "seafood",
        "shrimp",
        "tuna",
        "turkey",
        "whey",
        "yogurt",
    },
    "halal": {"alcohol", "bacon", "beer", "ham", "pork", "wine"},
    "kosher": {"bacon", "crab", "ham", "lobster", "pork", "shellfish", "shrimp"},
    "gluten_free": {"barley", "bread", "flour", "gluten", "noodle", "pasta", "rye", "wheat"},
    "gluten-free": {"barley", "bread", "flour", "gluten", "noodle", "pasta", "rye", "wheat"},
    "dairy_free": {"butter", "cheese", "cream", "dairy", "milk", "whey", "yogurt"},
    "dairy-free": {"butter", "cheese", "cream", "dairy", "milk", "whey", "yogurt"},
    "lactose_free": {"butter", "cheese", "cream", "dairy", "milk", "whey", "yogurt"},
    "lactose-free": {"butter", "cheese", "cream", "dairy", "milk", "whey", "yogurt"},
}

ALLERGY_FLAG_TERMS: dict[str, set[str]] = {
    "contains_peanut": {"peanut", "peanuts"},
    "contains_tree_nuts": {"tree nuts", "nuts", "almond", "walnut", "cashew"},
    "contains_shellfish": {"shellfish", "shrimp", "crab", "lobster"},
    "contains_fish": {"fish", "salmon", "tuna"},
    "contains_dairy": {"dairy", "milk", "lactose"},
    "contains_egg": {"egg", "eggs"},
    "contains_gluten": {"gluten", "wheat"},
    "contains_soy": {"soy"},
    "contains_sesame": {"sesame"},
}

DIET_TAG_BY_TERM: dict[str, str] = {
    "vegetarian": "vegetarian_candidate",
    "vegan": "vegan_candidate",
    "halal": "halal_candidate",
    "kosher": "kosher_candidate",
    "gluten_free": "gluten_free_candidate",
    "gluten-free": "gluten_free_candidate",
    "dairy_free": "dairy_free_candidate",
    "dairy-free": "dairy_free_candidate",
    "lactose_free": "dairy_free_candidate",
    "lactose-free": "dairy_free_candidate",
    "low_carb": "low_carb",
    "low-carb": "low_carb",
}

DIET_REJECTION_FLAGS: dict[str, set[str]] = {
    "halal": {"contains_pork", "contains_alcohol"},
    "kosher": {"contains_pork", "contains_shellfish"},
    "gluten_free": {"contains_gluten"},
    "gluten-free": {"contains_gluten"},
    "dairy_free": {"contains_dairy"},
    "dairy-free": {"contains_dairy"},
    "lactose_free": {"contains_dairy"},
    "lactose-free": {"contains_dairy"},
}

TEMPLATE_FALLBACK_NOTE = (
    "Fallback raw-food generation used because no matching meal template was found."
)
INSUFFICIENT_TEMPLATE_NOTE = (
    "Generated plan is below target because insufficient matching templates were available."
)


class MealPlanService:
    """
    Handles manual meal plan creation and rule-based meal plan generation.

    The generation logic is intentionally deterministic:
    - filters out broken/unusable food items
    - applies meal-slot suitability rules
    - uses weighted scoring per slot
    - keeps portion sizes within sane bounds
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------------------------
    # Basic fetch helpers
    # -------------------------------------------------------------------------

    def _get_active_goal(self, current_user: User) -> UserGoal:
        goal = self.db.scalar(
            select(UserGoal)
            .where(
                UserGoal.user_id == current_user.id,
                UserGoal.is_active.is_(True),
            )
            .order_by(desc(UserGoal.started_at))
        )

        if goal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active goal found for this user.",
            )

        return goal

    def _require_user_profile(self, current_user: User) -> UserProfile:
        profile = self.db.scalar(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
        )

        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile is required before generating a meal plan.",
            )

        return profile

    def _get_food_item(self, food_item_id: str) -> FoodItem:
        item = self.db.scalar(
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food item not found: {food_item_id}",
            )

        if item.nutrition_fact is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Food item {item.name} has no nutrition facts.",
            )

        return item

    def get_meal_plan(self, current_user: User, meal_plan_id: str) -> MealPlan:
        plan = self.db.scalar(
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == current_user.id,
            )
        )

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found.",
            )

        return plan

    def list_meal_plans(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MealPlan]:
        return list(
            self.db.scalars(
                select(MealPlan)
                .options(selectinload(MealPlan.items))
                .where(MealPlan.user_id == current_user.id)
                .order_by(desc(MealPlan.plan_date), desc(MealPlan.created_at))
                .offset(offset)
                .limit(limit)
            ).all()
        )

    # -------------------------------------------------------------------------
    # Nutrition / validation helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalized_name(item: FoodItem) -> str:
        return (item.name or "").strip().lower()

    @staticmethod
    def _normalized_category(item: FoodItem) -> str:
        return (item.category or "").strip().lower()

    @staticmethod
    def _normalize_term(value: str | None) -> str:
        return " ".join((value or "").strip().lower().split())

    def _food_search_text(self, item: FoodItem) -> str:
        fields: list[str] = [
            item.name or "",
            item.category or "",
            item.description or "",
            item.source or "",
            item.normalized_name or "",
            item.display_name or "",
            item.search_name or "",
        ]

        for optional_field in ("diet_type", "dietary_tags", "tags"):
            value = getattr(item, optional_field, None)
            if value:
                fields.append(str(value))

        for alias in item.aliases or []:
            fields.append(alias.alias_text or "")
            fields.append(alias.normalized_alias or "")

        return self._normalize_term(" ".join(fields))

    @staticmethod
    def _contains_any_term(search_text: str, terms: Iterable[str]) -> bool:
        for term in terms:
            if not term:
                continue
            if len(term) <= 3:
                if re.search(rf"\b{re.escape(term)}s?\b", search_text):
                    return True
            elif term in search_text:
                return True
        return False

    def _load_active_allergy_terms(self, current_user: User) -> list[str]:
        allergies = self.db.scalars(
            select(Allergy).where(
                Allergy.user_id == current_user.id,
                Allergy.is_active.is_(True),
            )
        ).all()
        return [
            term
            for term in (self._normalize_term(allergy.allergen_name) for allergy in allergies)
            if term
        ]

    def _load_active_preference_terms(self, current_user: User) -> dict[str, list[str]]:
        preferences = self.db.scalars(
            select(DietaryPreference).where(
                DietaryPreference.user_id == current_user.id,
                DietaryPreference.is_active.is_(True),
            )
        ).all()

        terms: dict[str, list[str]] = defaultdict(list)
        for preference in preferences:
            preference_type = self._normalize_term(preference.preference_type)
            value = self._normalize_term(preference.value)
            if preference_type and value:
                terms[preference_type].append(value)
        return dict(terms)

    def _validate_preferred_food_item_ids(self, preferred_food_item_ids: Iterable[str]) -> None:
        preferred_ids = [item_id for item_id in preferred_food_item_ids if item_id]
        if not preferred_ids:
            return

        found_ids = set(
            self.db.scalars(
                select(FoodItem.id).where(
                    FoodItem.id.in_(preferred_ids),
                    FoodItem.is_active.is_(True),
                )
            ).all()
        )
        missing_ids = sorted(set(preferred_ids) - found_ids)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid preferred_food_item_ids: {', '.join(missing_ids)}.",
            )

    def _validate_meal_slots(self, meal_slots: Iterable[str]) -> list[str]:
        normalized_slots = [
            self._normalize_term(meal_slot)
            for meal_slot in meal_slots
            if self._normalize_term(meal_slot)
        ]

        if not normalized_slots:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one meal slot is required.",
            )

        invalid_slots = sorted(set(normalized_slots) - VALID_MEAL_SLOTS)
        if invalid_slots:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid meal slot(s): {', '.join(invalid_slots)}.",
            )

        return normalized_slots

    def _is_food_item_usable_for_generation(self, item: FoodItem) -> bool:
        """
        Filters out broken or unrealistic food rows so garbage seed/test items
        do not pollute the generated plan.
        """
        if not item.is_active:
            return False

        nutrition = item.nutrition_fact
        if nutrition is None:
            return False

        name = self._normalized_name(item)
        if name in PLACEHOLDER_NAMES:
            return False

        calories = float(nutrition.calories_per_100g)
        protein = float(nutrition.protein_g_per_100g)
        carbs = float(nutrition.carbs_g_per_100g)
        fat = float(nutrition.fat_g_per_100g)

        if calories < 0 or calories > 900:
            return False

        if protein < 0 or protein > 100:
            return False
        if carbs < 0 or carbs > 100:
            return False
        if fat < 0 or fat > 100:
            return False

        # Impossible macro total per 100 g
        if protein + carbs + fat > 102:
            return False

        return True

    def _diet_or_restriction_excludes_food(
        self,
        item: FoodItem,
        diet_terms: Iterable[str],
    ) -> bool:
        search_text = self._food_search_text(item)

        for diet_term in diet_terms:
            forbidden_terms = DIET_FORBIDDEN_TERMS.get(
                diet_term,
                DIET_FORBIDDEN_TERMS.get(diet_term.replace(" ", "_")),
            )
            if forbidden_terms and self._contains_any_term(search_text, forbidden_terms):
                return True

        return False

    def _filter_candidates_for_preferences(
        self,
        candidates: list[FoodItem],
        allergy_terms: list[str],
        preference_terms: dict[str, list[str]],
    ) -> list[FoodItem]:
        disliked_terms = preference_terms.get("disliked_food", [])
        diet_terms = [
            *preference_terms.get("diet_type", []),
            *preference_terms.get("restriction", []),
        ]

        filtered: list[FoodItem] = []
        for item in candidates:
            search_text = self._food_search_text(item)

            if self._contains_any_term(search_text, allergy_terms):
                continue

            if self._contains_any_term(search_text, disliked_terms):
                continue

            if self._diet_or_restriction_excludes_food(item, diet_terms):
                continue

            filtered.append(item)

        if not filtered:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No candidate food items remained after allergy and preference "
                    "filtering."
                ),
            )

        return filtered

    @staticmethod
    def _normalized_slot_ratios(meal_slots: Iterable[str]) -> dict[str, float]:
        slots = list(meal_slots)
        total_ratio = sum(SLOT_CALORIE_SPLITS.get(slot, 0.25) for slot in slots)
        if total_ratio <= 0:
            return {slot: 1.0 / max(len(slots), 1) for slot in slots}
        return {
            slot: SLOT_CALORIE_SPLITS.get(slot, 0.25) / total_ratio
            for slot in slots
        }

    @classmethod
    def _slot_target_calories(
        cls,
        total_target_calories: float,
        meal_slot: str,
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        ratio = (
            slot_ratios.get(meal_slot, SLOT_CALORIE_SPLITS.get(meal_slot, 0.25))
            if slot_ratios is not None
            else SLOT_CALORIE_SPLITS.get(meal_slot, 0.25)
        )
        return round(total_target_calories * ratio, 2)

    @staticmethod
    def _slot_multiplier_bounds(meal_slot: str) -> tuple[float, float]:
        if meal_slot == "snack":
            return 0.5, 2.0
        return 0.75, 2.5

    @staticmethod
    def _slot_gram_bounds(meal_slot: str) -> tuple[float, float]:
        if meal_slot == "snack":
            return 30.0, 150.0
        if meal_slot == "breakfast":
            return 60.0, 250.0
        return 100.0, 320.0

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _calculate_macros_for_grams(item: FoodItem, grams: float) -> tuple[float, float, float, float]:
        nutrition = item.nutrition_fact
        assert nutrition is not None

        factor = grams / 100.0
        calories = round(float(nutrition.calories_per_100g) * factor, 2)
        protein = round(float(nutrition.protein_g_per_100g) * factor, 2)
        carbs = round(float(nutrition.carbs_g_per_100g) * factor, 2)
        fat = round(float(nutrition.fat_g_per_100g) * factor, 2)
        return calories, protein, carbs, fat

    def _planned_grams_for_slot(
        self,
        item: FoodItem,
        meal_slot: str,
        total_target_calories: float,
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        nutrition = item.nutrition_fact
        assert nutrition is not None

        calories_per_100g = float(nutrition.calories_per_100g)
        default_serving = float(item.default_serving_size_g or 100.0)

        minimum_grams, maximum_grams = self._slot_gram_bounds(meal_slot)

        if calories_per_100g <= 0:
            return round(self._clamp(default_serving, minimum_grams, maximum_grams), 2)

        slot_target_calories = self._slot_target_calories(
            total_target_calories,
            meal_slot,
            slot_ratios,
        )
        estimated_grams = (slot_target_calories / calories_per_100g) * 100.0

        # Blend slot target with the food's own default serving to avoid absurd sizes.
        blended_grams = (estimated_grams * 0.65) + (default_serving * 0.35)
        clamped = self._clamp(blended_grams, minimum_grams, maximum_grams)
        return round(clamped, 2)

    # -------------------------------------------------------------------------
    # Rule-based scoring helpers
    # -------------------------------------------------------------------------

    def _slot_rule_score(self, item: FoodItem, meal_slot: str) -> float:
        rules = SLOT_RULES.get(meal_slot, SLOT_RULES["lunch"])
        category = self._normalized_category(item)
        name = self._normalized_name(item)

        score = 0.0

        if category in rules["prefer_categories"]:
            score += 4.0
        if category in rules["avoid_categories"]:
            score -= 6.0

        for keyword in rules["prefer_keywords"]:
            if keyword in name:
                score += 2.5

        for keyword in rules["avoid_keywords"]:
            if keyword in name:
                score -= 5.0

        return score

    def _macro_density_score(self, item: FoodItem, meal_slot: str) -> float:
        nutrition = item.nutrition_fact
        assert nutrition is not None

        protein = float(nutrition.protein_g_per_100g)
        carbs = float(nutrition.carbs_g_per_100g)
        fat = float(nutrition.fat_g_per_100g)
        calories = float(nutrition.calories_per_100g)

        score = 0.0

        if meal_slot == "breakfast":
            score += protein * 0.10
            score += carbs * 0.03
            score -= max(0.0, fat - 25.0) * 0.08

        elif meal_slot in {"lunch", "dinner"}:
            score += protein * 0.12
            score += carbs * 0.04
            score -= max(0.0, fat - 35.0) * 0.06

        elif meal_slot == "snack":
            score += protein * 0.10
            score -= carbs * 0.04
            score -= max(0.0, fat - 20.0) * 0.08
            if calories > 250:
                score -= 2.0

        return score

    def _target_fit_score(
        self,
        item: FoodItem,
        meal_slot: str,
        active_goal: UserGoal,
        total_slots: int,
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        planned_grams = self._planned_grams_for_slot(
            item=item,
            meal_slot=meal_slot,
            total_target_calories=float(active_goal.target_calories),
            slot_ratios=slot_ratios,
        )
        calories, protein, carbs, fat = self._calculate_macros_for_grams(
            item,
            planned_grams,
        )

        slot_calorie_target = self._slot_target_calories(
            float(active_goal.target_calories),
            meal_slot,
            slot_ratios,
        )
        macro_ratio = (
            slot_ratios.get(meal_slot, 1.0 / max(total_slots, 1))
            if slot_ratios is not None
            else SLOT_CALORIE_SPLITS.get(meal_slot, 1.0 / max(total_slots, 1))
        )
        protein_target = float(active_goal.target_protein_g) * macro_ratio
        carbs_target = float(active_goal.target_carbs_g) * macro_ratio
        fat_target = float(active_goal.target_fat_g) * macro_ratio

        def fit(actual: float, target: float, weight: float) -> float:
            if target <= 0:
                return 0.0
            miss_ratio = abs(actual - target) / target
            return max(0.0, 1.0 - miss_ratio) * weight

        return (
            fit(calories, slot_calorie_target, 6.0)
            + fit(protein, protein_target, 3.0)
            + fit(carbs, carbs_target, 2.0)
            + fit(fat, fat_target, 2.0)
        )

    def _preferred_food_boost(
        self,
        item: FoodItem,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        score = 0.0
        if item.id in preferred_food_item_ids:
            score += 6.0

        search_text = self._food_search_text(item)
        for term in preferred_food_terms:
            if term and term in search_text:
                score += 4.0

        return score

    @staticmethod
    def _popularity_score(item: FoodItem) -> float:
        popularity = float(item.popularity_score or 0.0)
        usage_count = float(item.usage_count or 0.0)
        return min(popularity, 5.0) * 0.25 + min(usage_count, 100.0) * 0.015

    def _repetition_penalty(self, item: FoodItem, used_food_item_ids: set[str]) -> float:
        return -8.0 if item.id in used_food_item_ids else 0.0

    def _candidate_score(
        self,
        item: FoodItem,
        meal_slot: str,
        used_food_item_ids: set[str],
        active_goal: UserGoal,
        total_slots: int,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        return (
            self._slot_rule_score(item, meal_slot)
            + self._macro_density_score(item, meal_slot)
            + self._target_fit_score(item, meal_slot, active_goal, total_slots, slot_ratios)
            + self._preferred_food_boost(
                item,
                preferred_food_terms,
                preferred_food_item_ids,
            )
            + self._repetition_penalty(item, used_food_item_ids)
            + self._popularity_score(item)
        )

    # -------------------------------------------------------------------------
    # Template-based generation helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _json_dict(value: dict | None) -> dict:
        return value if isinstance(value, dict) else {}

    def _template_diet_tags(self, template: MealTemplate) -> dict:
        tags = dict(self._json_dict(template.recipe.diet_tags_json)) if template.recipe else {}
        tags.update(self._json_dict(template.diet_tags_json))
        return tags

    def _template_allergen_flags(self, template: MealTemplate) -> dict:
        flags: dict = {}
        if template.recipe is not None:
            flags.update(self._json_dict(template.recipe.allergen_flags_json))
        for flag, enabled in self._json_dict(template.allergen_flags_json).items():
            flags[flag] = bool(flags.get(flag)) or bool(enabled)
        return flags

    def _allergy_flags_from_terms(self, allergy_terms: Iterable[str]) -> set[str]:
        flags: set[str] = set()
        for term in allergy_terms:
            for flag, mapped_terms in ALLERGY_FLAG_TERMS.items():
                if self._contains_any_term(term, mapped_terms):
                    flags.add(flag)
        return flags

    def _template_text(self, template: MealTemplate) -> str:
        fields: list[str] = [
            template.name or "",
            template.category or "",
            template.diet_type or "",
            template.description or "",
            template.notes or "",
        ]
        if template.recipe is not None:
            fields.extend(
                [
                    template.recipe.name or "",
                    template.recipe.category or "",
                    template.recipe.diet_type or "",
                    template.recipe.description or "",
                ]
            )
            for ingredient in template.recipe.ingredients or []:
                fields.append(ingredient.ingredient_name_snapshot or "")
                if ingredient.food_item is not None:
                    fields.append(ingredient.food_item.name or "")
                    fields.append(ingredient.food_item.category or "")
        return self._normalize_term(" ".join(fields))

    def _template_has_usable_ingredients(self, template: MealTemplate) -> bool:
        if template.recipe is None or not template.recipe.is_active or not template.recipe.ingredients:
            return False
        return any(
            ingredient.food_item is not None
            and ingredient.food_item.is_active
            and ingredient.food_item.nutrition_fact is not None
            and float(ingredient.grams or 0) > 0
            for ingredient in template.recipe.ingredients
        )

    def _template_excluded_by_allergies(
        self,
        template: MealTemplate,
        allergy_flags: set[str],
    ) -> bool:
        flags = self._template_allergen_flags(template)
        return any(bool(flags.get(flag)) for flag in allergy_flags)

    def _template_satisfies_hard_diet_terms(
        self,
        template: MealTemplate,
        diet_terms: Iterable[str],
    ) -> bool:
        template_tags = self._template_diet_tags(template)
        template_flags = self._template_allergen_flags(template)

        for diet_term in diet_terms:
            normalized = diet_term.replace(" ", "_")
            if normalized in {"low_carb", "low-carb"}:
                continue

            restriction_flags = self._allergy_flags_from_terms([diet_term])
            if any(bool(template_flags.get(flag)) for flag in restriction_flags):
                return False

            if normalized in {"dairy_free", "dairy-free", "lactose_free", "lactose-free"}:
                if bool(template_flags.get("contains_dairy")):
                    return False
                continue

            if normalized in {"gluten_free", "gluten-free"}:
                if bool(template_tags.get("gluten_free_candidate")):
                    continue
                if bool(template_flags.get("contains_gluten")):
                    return False
                continue

            required_tag = DIET_TAG_BY_TERM.get(normalized)
            if required_tag and not bool(template_tags.get(required_tag)):
                return False

            for flag in DIET_REJECTION_FLAGS.get(normalized, set()):
                if bool(template_flags.get(flag)):
                    return False

            if normalized == "halal" and (
                bool(template_flags.get("contains_pork"))
                or bool(template_flags.get("contains_alcohol"))
            ):
                return False

        return True

    def _low_carb_requested(self, preference_terms: dict[str, list[str]]) -> bool:
        diet_terms = [
            *preference_terms.get("diet_type", []),
            *preference_terms.get("restriction", []),
        ]
        return any(term.replace(" ", "_") in {"low_carb", "low-carb"} for term in diet_terms)

    def _filter_templates_for_slot(
        self,
        templates: list[MealTemplate],
        meal_slot: str,
        allergy_terms: list[str],
        preference_terms: dict[str, list[str]],
    ) -> list[MealTemplate]:
        allergy_flags = self._allergy_flags_from_terms(allergy_terms)
        disliked_terms = preference_terms.get("disliked_food", [])
        diet_terms = [
            *preference_terms.get("diet_type", []),
            *preference_terms.get("restriction", []),
        ]

        filtered: list[MealTemplate] = []
        for template in templates:
            if self._normalize_term(template.meal_slot) != meal_slot:
                continue
            if not template.is_active or not self._template_has_usable_ingredients(template):
                continue
            if self._template_excluded_by_allergies(template, allergy_flags):
                continue
            if not self._template_satisfies_hard_diet_terms(template, diet_terms):
                continue
            if self._contains_any_term(self._template_text(template), disliked_terms):
                continue
            filtered.append(template)

        if self._low_carb_requested(preference_terms):
            low_carb = [
                template
                for template in filtered
                if bool(self._template_diet_tags(template).get("low_carb"))
            ]
            if low_carb:
                return low_carb

        return filtered

    def _load_template_generation_pool(self) -> list[MealTemplate]:
        return list(
            self.db.scalars(
                select(MealTemplate)
                .options(
                    selectinload(MealTemplate.recipe)
                    .selectinload(Recipe.ingredients)
                    .selectinload(RecipeIngredient.food_item)
                    .selectinload(FoodItem.nutrition_fact)
                )
                .where(MealTemplate.is_active.is_(True))
            ).all()
        )

    def _template_target_fit_score(
        self,
        template: MealTemplate,
        meal_slot: str,
        active_goal: UserGoal,
        total_slots: int,
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        macro_ratio = (
            slot_ratios.get(meal_slot, 1.0 / max(total_slots, 1))
            if slot_ratios is not None
            else SLOT_CALORIE_SPLITS.get(meal_slot, 1.0 / max(total_slots, 1))
        )
        calorie_target = self._slot_target_calories(
            float(active_goal.target_calories),
            meal_slot,
            slot_ratios,
        )
        protein_target = float(active_goal.target_protein_g) * macro_ratio
        carbs_target = float(active_goal.target_carbs_g) * macro_ratio
        fat_target = float(active_goal.target_fat_g) * macro_ratio

        def fit(actual: float | None, target: float, weight: float) -> float:
            if actual is None or target <= 0:
                return 0.0
            miss_ratio = abs(float(actual) - target) / target
            return max(0.0, 1.0 - miss_ratio) * weight

        return (
            fit(template.estimated_calories, calorie_target, 8.0)
            + fit(template.estimated_protein_g, protein_target, 4.0)
            + fit(template.estimated_carbs_g, carbs_target, 2.5)
            + fit(template.estimated_fat_g, fat_target, 2.5)
        )

    def _preferred_template_boost(
        self,
        template: MealTemplate,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
    ) -> float:
        score = 0.0
        search_text = self._template_text(template)
        for term in preferred_food_terms:
            if term and term in search_text:
                score += 5.0

        if template.recipe is not None:
            ingredient_food_ids = {
                ingredient.food_item_id
                for ingredient in template.recipe.ingredients or []
            }
            if ingredient_food_ids & preferred_food_item_ids:
                score += 8.0

        return score

    def _template_score(
        self,
        template: MealTemplate,
        meal_slot: str,
        active_goal: UserGoal,
        total_slots: int,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
        used_template_ids: set[str],
        used_recipe_ids: set[str],
        preference_terms: dict[str, list[str]],
        recent_source_usage: dict[str, int],
        slot_ratios: dict[str, float] | None = None,
    ) -> float:
        score = self._template_target_fit_score(
            template,
            meal_slot,
            active_goal,
            total_slots,
            slot_ratios,
        )
        score += self._preferred_template_boost(template, preferred_food_terms, preferred_food_item_ids)

        tags = self._template_diet_tags(template)
        if self._low_carb_requested(preference_terms) and bool(tags.get("low_carb")):
            score += 4.0

        if template.id in used_template_ids:
            score -= 100.0
        if template.recipe_id and template.recipe_id in used_recipe_ids:
            score -= 100.0
        score -= recent_source_usage.get(f"template:{template.id}", 0) * 12.0
        if template.recipe_id:
            score -= recent_source_usage.get(f"recipe:{template.recipe_id}", 0) * 12.0
        return score

    def _pick_best_template_for_slot(
        self,
        templates: list[MealTemplate],
        meal_slot: str,
        active_goal: UserGoal,
        total_slots: int,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
        used_template_ids: set[str],
        used_recipe_ids: set[str],
        preference_terms: dict[str, list[str]],
        recent_source_usage: dict[str, int],
        slot_ratios: dict[str, float] | None = None,
    ) -> MealTemplate | None:
        available = [
            template
            for template in templates
            if template.id not in used_template_ids
            and (not template.recipe_id or template.recipe_id not in used_recipe_ids)
        ]
        if not available:
            return None

        scored = sorted(
            (
                (
                    template,
                    self._template_score(
                        template=template,
                        meal_slot=meal_slot,
                        active_goal=active_goal,
                        total_slots=total_slots,
                        preferred_food_terms=preferred_food_terms,
                        preferred_food_item_ids=preferred_food_item_ids,
                        used_template_ids=used_template_ids,
                        used_recipe_ids=used_recipe_ids,
                        preference_terms=preference_terms,
                        recent_source_usage=recent_source_usage,
                        slot_ratios=slot_ratios,
                    ),
                )
                for template in available
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        best_score = scored[0][1]
        close_pool = [
            pair
            for pair in scored[:5]
            if best_score == 0 or pair[1] >= best_score * 0.85
        ]
        pool = close_pool or scored[:1]
        index = len(used_template_ids) % len(pool)
        return pool[index][0]

    def _load_recent_source_usage(self, current_user: User) -> dict[str, int]:
        usage: dict[str, int] = defaultdict(int)
        rows = self.db.execute(
            select(MealPlanItem.source_template_id, MealPlanItem.source_recipe_id)
            .join(MealPlan, MealPlanItem.meal_plan_id == MealPlan.id)
            .where(
                MealPlan.user_id == current_user.id,
                MealPlanItem.source_generation_type == "meal_template",
            )
        ).all()
        for template_id, recipe_id in rows:
            if template_id:
                usage[f"template:{template_id}"] += 1
            if recipe_id:
                usage[f"recipe:{recipe_id}"] += 1
        return dict(usage)

    def _load_generation_pool(
        self,
        preferred_food_item_ids: Iterable[str],
    ) -> list[FoodItem]:
        self._validate_preferred_food_item_ids(preferred_food_item_ids)

        candidates = list(
            self.db.scalars(
                select(FoodItem)
                .options(
                    selectinload(FoodItem.nutrition_fact),
                    selectinload(FoodItem.aliases),
                )
                .where(FoodItem.is_active.is_(True))
            ).all()
        )

        clean_candidates = [
            item for item in candidates if self._is_food_item_usable_for_generation(item)
        ]

        if not clean_candidates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No usable food items were available for rule-based generation. "
                    "Add realistic food items with valid nutrition facts first."
                ),
            )

        return clean_candidates

    def _pick_best_food_for_slot(
        self,
        meal_slot: str,
        candidates: list[FoodItem],
        used_food_item_ids: set[str],
        active_goal: UserGoal,
        total_slots: int,
        preferred_food_terms: Iterable[str],
        preferred_food_item_ids: set[str],
        slot_ratios: dict[str, float] | None = None,
    ) -> FoodItem:
        scored_pairs = sorted(
            (
                (
                    item,
                    self._candidate_score(
                        item=item,
                        meal_slot=meal_slot,
                        used_food_item_ids=used_food_item_ids,
                        active_goal=active_goal,
                        total_slots=total_slots,
                        preferred_food_terms=preferred_food_terms,
                        preferred_food_item_ids=preferred_food_item_ids,
                        slot_ratios=slot_ratios,
                    ),
                )
                for item in candidates
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )

        # Primary pass: only accept candidates that are not strongly incompatible
        primary = [
            item
            for item, score in scored_pairs
            if score > -1.0
        ]

        if primary:
            return primary[0]

        # Fallback pass: if catalog is tiny, at least pick the best remaining sane item
        return scored_pairs[0][0]

    def _template_base_macros(
        self,
        template: MealTemplate,
    ) -> tuple[float, float, float, float]:
        calories = protein = carbs = fat = 0.0
        if template.recipe is None:
            return 0.0, 0.0, 0.0, 0.0

        for ingredient in template.recipe.ingredients or []:
            food_item = ingredient.food_item
            if (
                food_item is None
                or food_item.nutrition_fact is None
                or float(ingredient.grams or 0) <= 0
            ):
                continue
            item_calories, item_protein, item_carbs, item_fat = self._calculate_macros_for_grams(
                food_item,
                float(ingredient.grams),
            )
            calories += item_calories
            protein += item_protein
            carbs += item_carbs
            fat += item_fat

        return (
            round(calories, 2),
            round(protein, 2),
            round(carbs, 2),
            round(fat, 2),
        )

    def _serving_multiplier_for_template(
        self,
        template: MealTemplate,
        meal_slot: str,
        slot_target_calories: float,
    ) -> float:
        base_calories, _protein, _carbs, _fat = self._template_base_macros(template)
        if base_calories <= 0:
            return 1.0

        minimum, maximum = self._slot_multiplier_bounds(meal_slot)
        multiplier = self._clamp(slot_target_calories / base_calories, minimum, maximum)
        max_allowed = maximum

        if template.recipe is not None:
            max_source_grams = max(
                (float(ingredient.grams or 0) for ingredient in template.recipe.ingredients or []),
                default=0.0,
            )
            if max_source_grams > 0:
                max_allowed = min(max_allowed, 600.0 / max_source_grams)

        slot_calorie_cap = max(1200.0, slot_target_calories * 1.15)
        max_allowed = min(max_allowed, slot_calorie_cap / base_calories)

        if max_allowed < minimum:
            multiplier = max_allowed
        else:
            multiplier = self._clamp(multiplier, minimum, max_allowed)

        return round(max(multiplier, 0.1), 2)

    @staticmethod
    def _target_status(total_calories: float, target_calories: float) -> str:
        if target_calories <= 0:
            return "within_target"
        ratio = total_calories / target_calories
        if ratio < 0.85:
            return "below_target"
        if ratio > 1.15:
            return "above_target"
        return "within_target"

    def _generation_metadata_note(
        self,
        active_goal: UserGoal,
        plan: MealPlan,
    ) -> str:
        target_calories = float(active_goal.target_calories)
        delta = round(plan.total_calories - target_calories, 2)
        delta_percent = round((delta / target_calories) * 100.0, 2) if target_calories > 0 else 0.0
        target_status = self._target_status(plan.total_calories, target_calories)
        return (
            "Generation target summary: "
            f"target_calories={round(target_calories, 2)}, "
            f"actual_calories={plan.total_calories}, "
            f"calorie_target_delta={delta}, "
            f"calorie_target_delta_percent={delta_percent}, "
            f"target_protein_g={round(float(active_goal.target_protein_g), 2)}, "
            f"actual_protein_g={plan.total_protein_g}, "
            f"target_carbs_g={round(float(active_goal.target_carbs_g), 2)}, "
            f"actual_carbs_g={plan.total_carbs_g}, "
            f"target_fat_g={round(float(active_goal.target_fat_g), 2)}, "
            f"actual_fat_g={plan.total_fat_g}, "
            f"target_status={target_status}."
        )

    @staticmethod
    def _append_plan_note(plan: MealPlan, note: str) -> None:
        plan.notes = f"{plan.notes}\n{note}" if plan.notes else note

    # -------------------------------------------------------------------------
    # Meal plan item builder
    # -------------------------------------------------------------------------

    def _build_meal_plan_item(
        self,
        meal_plan_id: str,
        food_item: FoodItem,
        meal_slot: str,
        position: int,
        planned_quantity: float,
        planned_grams: float,
        notes: str | None = None,
        source_generation_type: str | None = None,
    ) -> MealPlanItem:
        calories, protein, carbs, fat = self._calculate_macros_for_grams(
            food_item,
            planned_grams,
        )

        return MealPlanItem(
            meal_plan_id=meal_plan_id,
            food_item_id=food_item.id,
            meal_slot=meal_slot,
            position=position,
            food_name_snapshot=food_item.name,
            brand_snapshot=food_item.brand,
            planned_quantity=planned_quantity,
            planned_grams=planned_grams,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            notes=notes,
            source_generation_type=source_generation_type,
        )

    def _build_meal_plan_item_from_recipe_ingredient(
        self,
        meal_plan_id: str,
        ingredient: RecipeIngredient,
        meal_slot: str,
        position: int,
        recipe_name: str,
        template: MealTemplate,
        serving_multiplier: float = 1.0,
    ) -> MealPlanItem | None:
        food_item = ingredient.food_item
        if (
            food_item is None
            or not food_item.is_active
            or food_item.nutrition_fact is None
            or float(ingredient.grams or 0) <= 0
        ):
            return None

        planned_grams = round(float(ingredient.grams) * serving_multiplier, 2)
        default_serving = float(food_item.default_serving_size_g or 100.0)
        planned_quantity = round(planned_grams / default_serving, 2) if default_serving > 0 else 1.0
        calories, protein, carbs, fat = self._calculate_macros_for_grams(
            food_item,
            planned_grams,
        )

        return MealPlanItem(
            meal_plan_id=meal_plan_id,
            food_item_id=ingredient.food_item_id,
            meal_slot=meal_slot,
            position=position,
            food_name_snapshot=ingredient.ingredient_name_snapshot or food_item.name,
            brand_snapshot=food_item.brand,
            planned_quantity=planned_quantity,
            planned_grams=planned_grams,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            notes=f"From recipe: {recipe_name} | serving_multiplier={serving_multiplier:.2f}",
            source_recipe_id=ingredient.recipe_id,
            source_recipe_name=recipe_name,
            source_template_id=template.id,
            source_template_name=template.name,
            source_generation_type="meal_template",
        )

    @staticmethod
    def _apply_totals(plan: MealPlan, items: list[MealPlanItem]) -> None:
        plan.total_calories = round(sum(item.calories for item in items), 2)
        plan.total_protein_g = round(sum(item.protein_g for item in items), 2)
        plan.total_carbs_g = round(sum(item.carbs_g for item in items), 2)
        plan.total_fat_g = round(sum(item.fat_g for item in items), 2)
        plan.item_count = len(items)

    # -------------------------------------------------------------------------
    # Manual meal plans
    # -------------------------------------------------------------------------

    def create_meal_plan(
        self,
        current_user: User,
        payload: MealPlanCreateRequest,
    ) -> MealPlan:
        active_goal = self._get_active_goal(current_user)

        meal_plan = MealPlan(
            user_id=current_user.id,
            goal_id=active_goal.id,
            plan_date=payload.plan_date,
            generation_mode="manual",
            notes=payload.notes,
            total_calories=0,
            total_protein_g=0,
            total_carbs_g=0,
            total_fat_g=0,
            item_count=0,
        )
        self.db.add(meal_plan)
        self.db.flush()

        items: list[MealPlanItem] = []
        slot_positions: dict[str, int] = defaultdict(int)

        for entry in payload.items:
            food_item = self._get_food_item(entry.food_item_id)

            planned_grams = float(
                entry.planned_grams
                or food_item.default_serving_size_g
                or 100.0
            )
            planned_quantity = float(entry.planned_quantity)

            slot_positions[entry.meal_slot] += 1
            item = self._build_meal_plan_item(
                meal_plan_id=meal_plan.id,
                food_item=food_item,
                meal_slot=entry.meal_slot,
                position=slot_positions[entry.meal_slot],
                planned_quantity=planned_quantity,
                planned_grams=planned_grams,
                notes=entry.notes,
            )
            self.db.add(item)
            items.append(item)

        self._apply_totals(meal_plan, items)

        self.db.commit()
        self.db.refresh(meal_plan)
        return self.get_meal_plan(current_user, meal_plan.id)

    # -------------------------------------------------------------------------
    # Rule-based generation
    # -------------------------------------------------------------------------

    def generate_meal_plan(
        self,
        current_user: User,
        payload: MealPlanGenerateRequest,
    ) -> MealPlan:
        self._require_user_profile(current_user)
        active_goal = self._get_active_goal(current_user)

        meal_slots = self._validate_meal_slots(payload.meal_slots)
        self._validate_preferred_food_item_ids(payload.preferred_food_item_ids)
        allergy_terms = self._load_active_allergy_terms(current_user)
        preference_terms = self._load_active_preference_terms(current_user)

        max_items_per_slot = int(payload.max_items_per_slot or 1)
        if max_items_per_slot < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_items_per_slot must be at least 1.",
            )

        meal_plan = MealPlan(
            user_id=current_user.id,
            goal_id=active_goal.id,
            plan_date=payload.plan_date,
            generation_mode="rule_based",
            notes=payload.notes,
            total_calories=0,
            total_protein_g=0,
            total_carbs_g=0,
            total_fat_g=0,
            item_count=0,
        )
        self.db.add(meal_plan)
        self.db.flush()

        items: list[MealPlanItem] = []
        used_food_item_ids: set[str] = set()
        used_template_ids: set[str] = set()
        used_recipe_ids: set[str] = set()
        slot_positions: dict[str, int] = defaultdict(int)
        fallback_slots: set[str] = set()

        total_target_calories = float(active_goal.target_calories)
        preferred_food_terms = preference_terms.get("preferred_food", [])
        preferred_food_item_ids = set(payload.preferred_food_item_ids)
        total_slots = len(meal_slots)
        slot_ratios = self._normalized_slot_ratios(meal_slots)
        template_pool = self._load_template_generation_pool()
        recent_source_usage = self._load_recent_source_usage(current_user)
        raw_candidates: list[FoodItem] | None = None
        filler_templates_added = False

        def add_template_items(
            normalized_slot: str,
            selected_template: MealTemplate,
            slot_target_calories: float,
        ) -> int:
            if selected_template.recipe is None:
                return 0

            recipe = selected_template.recipe
            serving_multiplier = self._serving_multiplier_for_template(
                selected_template,
                normalized_slot,
                slot_target_calories,
            )
            created_for_template = 0
            for ingredient in recipe.ingredients:
                slot_positions[normalized_slot] += 1
                item = self._build_meal_plan_item_from_recipe_ingredient(
                    meal_plan_id=meal_plan.id,
                    ingredient=ingredient,
                    meal_slot=normalized_slot,
                    position=slot_positions[normalized_slot],
                    recipe_name=recipe.name,
                    template=selected_template,
                    serving_multiplier=serving_multiplier,
                )
                if item is None:
                    slot_positions[normalized_slot] -= 1
                    continue
                self.db.add(item)
                items.append(item)
                used_food_item_ids.add(item.food_item_id)
                created_for_template += 1

            if created_for_template:
                used_template_ids.add(selected_template.id)
                if selected_template.recipe_id:
                    used_recipe_ids.add(selected_template.recipe_id)
            return created_for_template

        for normalized_slot in meal_slots:
            slot_templates = self._filter_templates_for_slot(
                templates=template_pool,
                meal_slot=normalized_slot,
                allergy_terms=allergy_terms,
                preference_terms=preference_terms,
            )

            for _ in range(max_items_per_slot):
                selected_template = self._pick_best_template_for_slot(
                    templates=slot_templates,
                    meal_slot=normalized_slot,
                    active_goal=active_goal,
                    total_slots=total_slots,
                    preferred_food_terms=preferred_food_terms,
                    preferred_food_item_ids=preferred_food_item_ids,
                    used_template_ids=used_template_ids,
                    used_recipe_ids=used_recipe_ids,
                    preference_terms=preference_terms,
                    recent_source_usage=recent_source_usage,
                    slot_ratios=slot_ratios,
                )

                if selected_template is not None and selected_template.recipe is not None:
                    slot_target_calories = self._slot_target_calories(
                        total_target_calories,
                        normalized_slot,
                        slot_ratios,
                    )
                    created_for_template = add_template_items(
                        normalized_slot,
                        selected_template,
                        slot_target_calories,
                    )

                    if created_for_template:
                        continue

                fallback_slots.add(normalized_slot)
                if raw_candidates is None:
                    raw_candidates = self._load_generation_pool(payload.preferred_food_item_ids)
                    raw_candidates = self._filter_candidates_for_preferences(
                        candidates=raw_candidates,
                        allergy_terms=allergy_terms,
                        preference_terms=preference_terms,
                    )

                selected = self._pick_best_food_for_slot(
                    meal_slot=normalized_slot,
                    candidates=raw_candidates,
                    used_food_item_ids=used_food_item_ids,
                    active_goal=active_goal,
                    total_slots=total_slots,
                    preferred_food_terms=preferred_food_terms,
                    preferred_food_item_ids=preferred_food_item_ids,
                    slot_ratios=slot_ratios,
                )

                planned_grams = self._planned_grams_for_slot(
                    item=selected,
                    meal_slot=normalized_slot,
                    total_target_calories=total_target_calories,
                    slot_ratios=slot_ratios,
                )
                default_serving = float(selected.default_serving_size_g or 100.0)
                planned_quantity = round(planned_grams / default_serving, 2) if default_serving > 0 else 1.0

                slot_positions[normalized_slot] += 1
                item = self._build_meal_plan_item(
                    meal_plan_id=meal_plan.id,
                    food_item=selected,
                    meal_slot=normalized_slot,
                    position=slot_positions[normalized_slot],
                    planned_quantity=planned_quantity,
                    planned_grams=planned_grams,
                    notes=TEMPLATE_FALLBACK_NOTE,
                    source_generation_type="raw_food_fallback",
                )
                self.db.add(item)
                items.append(item)
                used_food_item_ids.add(selected.id)

        self._apply_totals(meal_plan, items)

        filler_slot_order = [
            slot for slot in ["snack", "lunch", "dinner", "breakfast"] if slot in meal_slots
        ] or meal_slots
        filler_attempt_limit = max(len(template_pool), 1)
        filler_attempts = 0
        while (
            self._target_status(meal_plan.total_calories, total_target_calories) == "below_target"
            and filler_attempts < filler_attempt_limit
        ):
            filler_attempts += 1
            added_this_round = False
            for filler_slot in filler_slot_order:
                if self._target_status(meal_plan.total_calories, total_target_calories) != "below_target":
                    break

                slot_templates = self._filter_templates_for_slot(
                    templates=template_pool,
                    meal_slot=filler_slot,
                    allergy_terms=allergy_terms,
                    preference_terms=preference_terms,
                )
                selected_template = self._pick_best_template_for_slot(
                    templates=slot_templates,
                    meal_slot=filler_slot,
                    active_goal=active_goal,
                    total_slots=total_slots,
                    preferred_food_terms=preferred_food_terms,
                    preferred_food_item_ids=preferred_food_item_ids,
                    used_template_ids=used_template_ids,
                    used_recipe_ids=used_recipe_ids,
                    preference_terms=preference_terms,
                    recent_source_usage=recent_source_usage,
                    slot_ratios=slot_ratios,
                )
                if selected_template is None:
                    continue

                remaining_calories = max(
                    0.0,
                    (total_target_calories * 0.95) - meal_plan.total_calories,
                )
                slot_target_calories = remaining_calories or self._slot_target_calories(
                    total_target_calories,
                    filler_slot,
                    slot_ratios,
                )
                created_for_template = add_template_items(
                    filler_slot,
                    selected_template,
                    slot_target_calories,
                )
                if created_for_template:
                    self._apply_totals(meal_plan, items)
                    filler_templates_added = True
                    added_this_round = True
                    break

            if not added_this_round:
                break

        if fallback_slots:
            fallback_note = (
                f"{TEMPLATE_FALLBACK_NOTE} Slot(s): {', '.join(sorted(fallback_slots))}."
            )
            self._append_plan_note(meal_plan, fallback_note)

        if filler_templates_added:
            self._append_plan_note(
                meal_plan,
                "Additional target-filler meal templates were added to improve calorie coverage.",
            )

        self._apply_totals(meal_plan, items)
        if self._target_status(meal_plan.total_calories, total_target_calories) == "below_target":
            self._append_plan_note(meal_plan, INSUFFICIENT_TEMPLATE_NOTE)
        self._append_plan_note(
            meal_plan,
            self._generation_metadata_note(active_goal, meal_plan),
        )

        self.db.commit()
        self.db.refresh(meal_plan)
        return self.get_meal_plan(current_user, meal_plan.id)
