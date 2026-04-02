from __future__ import annotations

from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.grocery_list import GroceryList
from app.models.grocery_list_item import GroceryListItem
from app.models.meal_plan import MealPlan
from app.models.user import User
from app.schemas.grocery import (
    GroceryListGenerateFromMealPlanRequest,
    GroceryListItemUpdateRequest,
)


class GroceryService:
    """
    Handles grocery list generation from meal plans and item state updates.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_meal_plan(
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
        meal_plan = self.db.scalar(statement)

        if meal_plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found.",
            )

        return meal_plan

    def _get_food_item_map(self, food_item_ids: list[str]) -> dict[str, FoodItem]:
        if not food_item_ids:
            return {}

        items = list(
            self.db.scalars(
                select(FoodItem).where(FoodItem.id.in_(food_item_ids))
            ).all()
        )
        return {item.id: item for item in items}

    def generate_from_meal_plan(
        self,
        current_user: User,
        payload: GroceryListGenerateFromMealPlanRequest,
    ) -> GroceryList:
        meal_plan = self._get_meal_plan(current_user, payload.meal_plan_id)

        if not meal_plan.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meal plan has no items to convert into a grocery list.",
            )

        food_item_ids = [item.food_item_id for item in meal_plan.items]
        food_item_map = self._get_food_item_map(food_item_ids)

        aggregated: dict[str, dict] = defaultdict(
            lambda: {
                "food_item_id": None,
                "item_name_snapshot": "",
                "category_snapshot": None,
                "total_grams": 0.0,
            }
        )

        for plan_item in meal_plan.items:
            bucket = aggregated[plan_item.food_item_id]
            bucket["food_item_id"] = plan_item.food_item_id
            bucket["item_name_snapshot"] = plan_item.food_name_snapshot

            food_item = food_item_map.get(plan_item.food_item_id)
            bucket["category_snapshot"] = food_item.category if food_item else None
            bucket["total_grams"] += plan_item.planned_grams

        grocery_list = GroceryList(
            user_id=current_user.id,
            meal_plan_id=meal_plan.id,
            title=payload.title.strip() if payload.title else f"Grocery list for {meal_plan.plan_date}",
            list_date=payload.list_date,
            source_type="meal_plan",
            status="active",
            notes=payload.notes.strip() if payload.notes else None,
            item_count=0,
        )

        for index, data in enumerate(
            sorted(aggregated.values(), key=lambda item: item["item_name_snapshot"].lower()),
            start=1,
        ):
            total_grams = round(float(data["total_grams"]), 2)

            grocery_item = GroceryListItem(
                food_item_id=data["food_item_id"],
                position=index,
                item_name_snapshot=data["item_name_snapshot"],
                category_snapshot=data["category_snapshot"],
                total_grams=total_grams,
                quantity_label=f"{total_grams} g",
                is_checked=False,
            )
            grocery_list.items.append(grocery_item)

        grocery_list.item_count = len(grocery_list.items)

        self.db.add(grocery_list)
        self.db.commit()
        self.db.refresh(grocery_list)

        return self.get_grocery_list(current_user, grocery_list.id)

    def list_grocery_lists(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> list[GroceryList]:
        statement: Select[tuple[GroceryList]] = (
            select(GroceryList)
            .options(selectinload(GroceryList.items))
            .where(GroceryList.user_id == current_user.id)
            .order_by(desc(GroceryList.list_date), desc(GroceryList.created_at))
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_grocery_list(
        self,
        current_user: User,
        grocery_list_id: str,
    ) -> GroceryList:
        statement = (
            select(GroceryList)
            .options(selectinload(GroceryList.items))
            .where(
                GroceryList.id == grocery_list_id,
                GroceryList.user_id == current_user.id,
            )
        )
        grocery_list = self.db.scalar(statement)

        if grocery_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grocery list not found.",
            )

        return grocery_list

    def update_grocery_list_item(
        self,
        current_user: User,
        grocery_list_item_id: str,
        payload: GroceryListItemUpdateRequest,
    ) -> GroceryListItem:
        statement = (
            select(GroceryListItem)
            .join(GroceryList, GroceryList.id == GroceryListItem.grocery_list_id)
            .where(
                GroceryListItem.id == grocery_list_item_id,
                GroceryList.user_id == current_user.id,
            )
        )
        item = self.db.scalar(statement)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grocery list item not found.",
            )

        item.is_checked = payload.is_checked

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item