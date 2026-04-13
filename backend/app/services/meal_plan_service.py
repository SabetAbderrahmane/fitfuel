from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.user import User
from app.models.user_goal import UserGoal
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

    def _macro_score(self, item: FoodItem, meal_slot: str) -> float:
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

    def _repetition_penalty(self, item: FoodItem, used_food_item_ids: set[str]) -> float:
        return -3.0 if item.id in used_food_item_ids else 0.0

    def _candidate_score(
        self,
        item: FoodItem,
        meal_slot: str,
        used_food_item_ids: set[str],
    ) -> float:
        return (
            self._slot_rule_score(item, meal_slot)
            + self._macro_score(item, meal_slot)
            + self._repetition_penalty(item, used_food_item_ids)
        )

    def _load_generation_pool(
        self,
        preferred_food_item_ids: Iterable[str],
    ) -> list[FoodItem]:
        preferred_ids = [item_id for item_id in preferred_food_item_ids if item_id]

        if preferred_ids:
            candidates = list(
                self.db.scalars(
                    select(FoodItem)
                    .options(selectinload(FoodItem.nutrition_fact))
                    .where(
                        FoodItem.id.in_(preferred_ids),
                        FoodItem.is_active.is_(True),
                    )
                ).all()
            )
        else:
            candidates = list(
                self.db.scalars(
                    select(FoodItem)
                    .options(selectinload(FoodItem.nutrition_fact))
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
    ) -> FoodItem:
        scored = sorted(
            candidates,
            key=lambda item: self._candidate_score(item, meal_slot, used_food_item_ids),
            reverse=True,
        )

        # Primary pass: only accept candidates that are not strongly incompatible
        primary = [
            item
            for item in scored
            if self._candidate_score(item, meal_slot, used_food_item_ids) > -1.0
        ]

        if primary:
            return primary[0]

        # Fallback pass: if catalog is tiny, at least pick the best remaining sane item
        return scored[0]

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
        active_goal = self._get_active_goal(current_user)

        candidates = self._load_generation_pool(payload.preferred_food_item_ids)
        if not payload.meal_slots:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one meal slot is required.",
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

        for meal_slot in payload.meal_slots:
            normalized_slot = meal_slot.strip().lower()

            for _ in range(max_items_per_slot):
                selected = self._pick_best_food_for_slot(
                    meal_slot=normalized_slot,
                    candidates=candidates,
                    used_food_item_ids=used_food_item_ids,
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