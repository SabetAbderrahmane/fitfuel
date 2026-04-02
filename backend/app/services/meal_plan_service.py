from collections import defaultdict
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.user import User
from app.models.user_goal import UserGoal
from app.schemas.meal_plan import MealPlanCreateRequest, MealPlanGenerateRequest, MealSlot


class MealPlanService:
    """
    Handles manual meal plans and a simple rule-based daily planner.

    This is intentionally lightweight for the current phase.
    We can replace or extend the generation logic later with a stronger
    optimizer or recommender.
    """

    SLOT_CALORIE_WEIGHTS: dict[str, float] = {
        "breakfast": 0.25,
        "lunch": 0.30,
        "dinner": 0.30,
        "snack": 0.15,
    }

    SLOT_CATEGORY_HINTS: dict[str, set[str]] = {
        "breakfast": {"breakfast", "fruit", "dairy", "egg", "cereal", "oats"},
        "lunch": {"lunch", "protein", "meat", "fish", "rice", "grain", "vegetable"},
        "dinner": {"dinner", "protein", "meat", "fish", "rice", "grain", "vegetable"},
        "snack": {"snack", "fruit", "dairy", "nuts", "bar"},
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_active_goal(self, user_id: str) -> UserGoal:
        goal = self.db.scalar(
            select(UserGoal)
            .where(
                UserGoal.user_id == user_id,
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

    def _get_food_item_with_nutrition(self, food_item_id: str) -> FoodItem:
        statement = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )
        item = self.db.scalar(statement)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food item not found: {food_item_id}",
            )

        if item.nutrition_fact is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Food item has no nutrition facts: {item.name}",
            )

        return item

    def _list_food_items_with_nutrition(
        self,
        preferred_food_item_ids: list[str] | None = None,
    ) -> list[FoodItem]:
        statement: Select[tuple[FoodItem]] = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(FoodItem.is_active.is_(True))
            .order_by(FoodItem.name.asc())
        )

        items = list(self.db.scalars(statement).all())
        items = [item for item in items if item.nutrition_fact is not None]

        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No food items with nutrition facts are available yet.",
            )

        if preferred_food_item_ids:
            preferred_set = set(preferred_food_item_ids)
            preferred_items = [item for item in items if item.id in preferred_set]
            other_items = [item for item in items if item.id not in preferred_set]
            items = preferred_items + other_items

        return items

    @staticmethod
    def _scale_nutrient(per_100g: float, grams: float) -> float:
        return round((grams / 100.0) * per_100g, 2)

    @staticmethod
    def _resolve_manual_grams(
        food_item: FoodItem,
        planned_grams: float | None,
        planned_quantity: float,
    ) -> float:
        if planned_grams is not None:
            return round(planned_grams, 2)

        if food_item.default_serving_size_g is not None:
            return round(food_item.default_serving_size_g * planned_quantity, 2)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Food item '{food_item.name}' requires planned_grams because it has "
                "no default serving size."
            ),
        )

    def _build_plan_item(
        self,
        food_item: FoodItem,
        meal_slot: MealSlot,
        position: int,
        planned_quantity: float,
        planned_grams: float,
        notes: str | None = None,
    ) -> MealPlanItem:
        nutrition = food_item.nutrition_fact
        assert nutrition is not None

        calories = self._scale_nutrient(nutrition.calories_per_100g, planned_grams)
        protein_g = self._scale_nutrient(nutrition.protein_g_per_100g, planned_grams)
        carbs_g = self._scale_nutrient(nutrition.carbs_g_per_100g, planned_grams)
        fat_g = self._scale_nutrient(nutrition.fat_g_per_100g, planned_grams)

        return MealPlanItem(
            food_item_id=food_item.id,
            meal_slot=meal_slot,
            position=position,
            food_name_snapshot=food_item.name,
            brand_snapshot=food_item.brand,
            planned_quantity=round(planned_quantity, 2),
            planned_grams=round(planned_grams, 2),
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            notes=notes.strip() if notes else None,
        )

    @staticmethod
    def _apply_plan_totals(plan: MealPlan) -> None:
        plan.total_calories = round(sum(item.calories for item in plan.items), 2)
        plan.total_protein_g = round(sum(item.protein_g for item in plan.items), 2)
        plan.total_carbs_g = round(sum(item.carbs_g for item in plan.items), 2)
        plan.total_fat_g = round(sum(item.fat_g for item in plan.items), 2)
        plan.item_count = len(plan.items)

    @staticmethod
    def _normalize_slot_weights(slots: Iterable[str]) -> dict[str, float]:
        requested = list(slots)
        total = sum(MealPlanService.SLOT_CALORIE_WEIGHTS.get(slot, 0.0) for slot in requested)

        if total <= 0:
            equal_weight = 1.0 / len(requested)
            return {slot: equal_weight for slot in requested}

        return {
            slot: MealPlanService.SLOT_CALORIE_WEIGHTS.get(slot, 0.0) / total
            for slot in requested
        }

    def create_manual_plan(
        self,
        current_user: User,
        payload: MealPlanCreateRequest,
    ) -> MealPlan:
        active_goal = self._get_active_goal(current_user.id)

        plan = MealPlan(
            user_id=current_user.id,
            goal_id=active_goal.id,
            plan_date=payload.plan_date,
            generation_mode="manual",
            notes=payload.notes.strip() if payload.notes else None,
        )

        position_counter: dict[str, int] = defaultdict(int)

        for item_payload in payload.items:
            food_item = self._get_food_item_with_nutrition(item_payload.food_item_id)
            position_counter[item_payload.meal_slot] += 1

            grams = self._resolve_manual_grams(
                food_item=food_item,
                planned_grams=item_payload.planned_grams,
                planned_quantity=item_payload.planned_quantity,
            )

            plan_item = self._build_plan_item(
                food_item=food_item,
                meal_slot=item_payload.meal_slot,
                position=position_counter[item_payload.meal_slot],
                planned_quantity=item_payload.planned_quantity,
                planned_grams=grams,
                notes=item_payload.notes,
            )
            plan.items.append(plan_item)

        self._apply_plan_totals(plan)

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return self.get_meal_plan(current_user=current_user, meal_plan_id=plan.id)

    @staticmethod
    def _slot_category_bonus(food_item: FoodItem, meal_slot: str) -> float:
        category = (food_item.category or "").strip().lower()
        if not category:
            return 0.0

        hints = MealPlanService.SLOT_CATEGORY_HINTS.get(meal_slot, set())
        return 15.0 if category in hints else 0.0

    @staticmethod
    def _protein_density_bonus(food_item: FoodItem) -> float:
        nutrition = food_item.nutrition_fact
        if nutrition is None:
            return 0.0
        return min(nutrition.protein_g_per_100g, 40.0)

    @staticmethod
    def _estimate_planned_grams(food_item: FoodItem, slot_target_calories: float) -> float:
        nutrition = food_item.nutrition_fact
        if nutrition is None or nutrition.calories_per_100g <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Food item '{food_item.name}' has invalid calories_per_100g.",
            )

        grams = (slot_target_calories / nutrition.calories_per_100g) * 100.0

        # Keep the starter planner realistic enough for MVP behavior.
        grams = max(60.0, min(grams, 450.0))
        return round(grams, 2)

    def generate_simple_plan(
        self,
        current_user: User,
        payload: MealPlanGenerateRequest,
    ) -> MealPlan:
        active_goal = self._get_active_goal(current_user.id)
        candidates = self._list_food_items_with_nutrition(payload.preferred_food_item_ids)

        slot_weights = self._normalize_slot_weights(payload.meal_slots)
        used_food_ids: set[str] = set()

        plan = MealPlan(
            user_id=current_user.id,
            goal_id=active_goal.id,
            plan_date=payload.plan_date,
            generation_mode="rule_based",
            notes=payload.notes.strip() if payload.notes else None,
        )

        position_counter: dict[str, int] = defaultdict(int)

        for meal_slot in payload.meal_slots:
            slot_target_calories = active_goal.target_calories * slot_weights[meal_slot]

            selected_for_slot = 0
            available_candidates = [item for item in candidates if item.nutrition_fact is not None]

            # Prefer unused foods first. If catalog is small, allow reuse as fallback.
            ranked_candidates = sorted(
                available_candidates,
                key=lambda item: (
                    item.id in used_food_ids,
                    -self._slot_category_bonus(item, meal_slot),
                    -self._protein_density_bonus(item),
                    item.name.lower(),
                ),
            )

            for candidate in ranked_candidates:
                if selected_for_slot >= payload.max_items_per_slot:
                    break

                position_counter[meal_slot] += 1

                per_item_target = slot_target_calories / payload.max_items_per_slot
                planned_grams = self._estimate_planned_grams(candidate, per_item_target)

                plan_item = self._build_plan_item(
                    food_item=candidate,
                    meal_slot=meal_slot,
                    position=position_counter[meal_slot],
                    planned_quantity=1.0,
                    planned_grams=planned_grams,
                    notes=None,
                )
                plan.items.append(plan_item)
                used_food_ids.add(candidate.id)
                selected_for_slot += 1

            if selected_for_slot == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not generate items for slot '{meal_slot}'.",
                )

        self._apply_plan_totals(plan)

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return self.get_meal_plan(current_user=current_user, meal_plan_id=plan.id)

    def list_meal_plans(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MealPlan]:
        statement: Select[tuple[MealPlan]] = (
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(MealPlan.user_id == current_user.id)
            .order_by(desc(MealPlan.plan_date), desc(MealPlan.created_at))
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_meal_plan(
        self,
        current_user: User,
        meal_plan_id: str,
    ) -> MealPlan:
        statement = (
            select(MealPlan)
            .options(selectinload(MealPlan.items))
            .where(
                MealPlan.id == meal_plan_id,
                MealPlan.user_id == current_user.id,
            )
        )
        plan = self.db.scalar(statement)

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found.",
            )

        return plan