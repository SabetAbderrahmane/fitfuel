from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.recipe import Recipe
from app.repositories.base import BaseRepository


class MealRepository(BaseRepository[FoodItem]):
    """
    Repository for food catalog and recipe retrieval used by meal-related services.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db, FoodItem)

    def get_food_item_with_nutrition(self, food_item_id: str) -> FoodItem | None:
        return self.db.scalar(
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )

    def list_food_items(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[FoodItem]:
        statement = (
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
                or_(
                    FoodItem.name.ilike(pattern),
                    FoodItem.brand.ilike(pattern),
                    FoodItem.category.ilike(pattern),
                )
            )

        return list(self.db.scalars(statement).all())

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        return self.db.scalar(
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .where(
                Recipe.id == recipe_id,
                Recipe.is_active.is_(True),
            )
        )

    def list_recipes(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        diet_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Recipe]:
        statement = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .where(Recipe.is_active.is_(True))
            .order_by(Recipe.name.asc())
            .offset(offset)
            .limit(limit)
        )

        if category:
            statement = statement.where(
                func.lower(Recipe.category) == category.strip().lower()
            )

        if diet_type:
            statement = statement.where(
                func.lower(Recipe.diet_type) == diet_type.strip().lower()
            )

        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                or_(
                    Recipe.name.ilike(pattern),
                    Recipe.description.ilike(pattern),
                    Recipe.category.ilike(pattern),
                    Recipe.diet_type.ilike(pattern),
                )
            )

        return list(self.db.scalars(statement).all())