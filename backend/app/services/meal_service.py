import re

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.nutrition_fact import NutritionFact
from app.schemas.meal import FoodItemCreateRequest


class MealService:
    """
    Food catalog and nutrition lookup service.

    This is the backend base for:
    - manual food logging
    - meal planning
    - AI nutrition matching after photo classification
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-{2,}", "-", value)
        return value.strip("-") or "food-item"

    def _generate_unique_slug(self, name: str, brand: str | None = None) -> str:
        base = self._slugify(f"{name}-{brand}" if brand else name)
        slug = base
        counter = 2

        while self.db.scalar(select(FoodItem).where(FoodItem.slug == slug)) is not None:
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    def create_food_item(self, payload: FoodItemCreateRequest) -> FoodItem:
        slug = self._generate_unique_slug(
            name=payload.name,
            brand=payload.brand,
        )

        food_item = FoodItem(
            name=payload.name.strip(),
            slug=slug,
            brand=payload.brand.strip() if payload.brand else None,
            category=payload.category.strip() if payload.category else None,
            description=payload.description.strip() if payload.description else None,
            default_serving_size_g=payload.default_serving_size_g,
            default_serving_label=(
                payload.default_serving_label.strip()
                if payload.default_serving_label
                else None
            ),
            source=payload.source.strip().lower(),
            is_active=True,
        )

        nutrition_fact = NutritionFact(
            calories_per_100g=payload.nutrition.calories_per_100g,
            protein_g_per_100g=payload.nutrition.protein_g_per_100g,
            carbs_g_per_100g=payload.nutrition.carbs_g_per_100g,
            fat_g_per_100g=payload.nutrition.fat_g_per_100g,
            fiber_g_per_100g=payload.nutrition.fiber_g_per_100g,
            sugar_g_per_100g=payload.nutrition.sugar_g_per_100g,
            sodium_mg_per_100g=payload.nutrition.sodium_mg_per_100g,
        )

        food_item.nutrition_fact = nutrition_fact

        self.db.add(food_item)
        self.db.commit()
        self.db.refresh(food_item)

        return food_item

    def list_food_items(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[FoodItem]:
        statement: Select[tuple[FoodItem]] = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(FoodItem.is_active.is_(True))
            .order_by(FoodItem.name.asc())
            .offset(offset)
            .limit(limit)
        )

        if category:
            statement = statement.where(
                func.lower(FoodItem.category) == category.strip().lower()
            )

        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                (FoodItem.name.ilike(pattern))
                | (FoodItem.brand.ilike(pattern))
                | (FoodItem.category.ilike(pattern))
            )

        return list(self.db.scalars(statement).all())

    def get_food_item(self, food_item_id: str) -> FoodItem:
        statement = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(FoodItem.id == food_item_id, FoodItem.is_active.is_(True))
        )
        food_item = self.db.scalar(statement)

        if food_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found.",
            )

        return food_item