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
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.meal_plan import (
    MealPlanCreateRequest,
    MealPlanGenerateRequest,
)


SLOT_CALORIE_SPLITS: dict[str, float] = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snack": 0.10,
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
    def _slot_target_calories(total_target_calories: float, meal_slot: str) -> float:
        ratio = SLOT_CALORIE_SPLITS.get(meal_slot, 0.25)
        return round(total_target_calories * ratio, 2)

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
    ) -> float:
        nutrition = item.nutrition_fact
        assert nutrition is not None

        calories_per_100g = float(nutrition.calories_per_100g)
        default_serving = float(item.default_serving_size_g or 100.0)

        minimum_grams, maximum_grams = self._slot_gram_bounds(meal_slot)

        if calories_per_100g <= 0:
            return round(self._clamp(default_serving, minimum_grams, maximum_grams), 2)

        slot_target_calories = self._slot_target_calories(total_target_calories, meal_slot)
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
    ) -> float:
        planned_grams = self._planned_grams_for_slot(
            item=item,
            meal_slot=meal_slot,
            total_target_calories=float(active_goal.target_calories),
        )
        calories, protein, carbs, fat = self._calculate_macros_for_grams(
            item,
            planned_grams,
        )

        slot_calorie_target = self._slot_target_calories(
            float(active_goal.target_calories),
            meal_slot,
        )
        macro_ratio = SLOT_CALORIE_SPLITS.get(meal_slot, 1.0 / max(total_slots, 1))
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
    ) -> float:
        return (
            self._slot_rule_score(item, meal_slot)
            + self._macro_density_score(item, meal_slot)
            + self._target_fit_score(item, meal_slot, active_goal, total_slots)
            + self._preferred_food_boost(
                item,
                preferred_food_terms,
                preferred_food_item_ids,
            )
            + self._repetition_penalty(item, used_food_item_ids)
            + self._popularity_score(item)
        )

    def _load_generation_pool(
        self,
        preferred_food_item_ids: Iterable[str],
    ) -> list[FoodItem]:
        preferred_ids = [item_id for item_id in preferred_food_item_ids if item_id]

        if preferred_ids:
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
        candidates = self._load_generation_pool(payload.preferred_food_item_ids)
        allergy_terms = self._load_active_allergy_terms(current_user)
        preference_terms = self._load_active_preference_terms(current_user)
        candidates = self._filter_candidates_for_preferences(
            candidates=candidates,
            allergy_terms=allergy_terms,
            preference_terms=preference_terms,
        )

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
        slot_positions: dict[str, int] = defaultdict(int)

        total_target_calories = float(active_goal.target_calories)
        preferred_food_terms = preference_terms.get("preferred_food", [])
        preferred_food_item_ids = set(payload.preferred_food_item_ids)
        total_slots = len(meal_slots)

        for normalized_slot in meal_slots:
            for _ in range(max_items_per_slot):
                selected = self._pick_best_food_for_slot(
                    meal_slot=normalized_slot,
                    candidates=candidates,
                    used_food_item_ids=used_food_item_ids,
                    active_goal=active_goal,
                    total_slots=total_slots,
                    preferred_food_terms=preferred_food_terms,
                    preferred_food_item_ids=preferred_food_item_ids,
                )

                planned_grams = self._planned_grams_for_slot(
                    item=selected,
                    meal_slot=normalized_slot,
                    total_target_calories=total_target_calories,
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
                    notes=None,
                )
                self.db.add(item)
                items.append(item)
                used_food_item_ids.add(selected.id)

        self._apply_totals(meal_plan, items)

        self.db.commit()
        self.db.refresh(meal_plan)
        return self.get_meal_plan(current_user, meal_plan.id)
