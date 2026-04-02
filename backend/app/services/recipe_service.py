from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.food_item import FoodItem
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.user import User
from app.schemas.recipe import RecipeCreateRequest


class RecipeService:
    """
    Handles recipe creation and lookup.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-{2,}", "-", value)
        return value.strip("-") or "recipe"

    def _generate_unique_slug(self, name: str) -> str:
        base = self._slugify(name)
        slug = base
        counter = 2

        while self.db.scalar(select(Recipe).where(Recipe.slug == slug)) is not None:
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    def _get_food_item_with_nutrition(self, food_item_id: str) -> FoodItem:
        statement = (
            select(FoodItem)
            .options(selectinload(FoodItem.nutrition_fact))
            .where(
                FoodItem.id == food_item_id,
                FoodItem.is_active.is_(True),
            )
        )
        food_item = self.db.scalar(statement)

        if food_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food item not found: {food_item_id}",
            )

        if food_item.nutrition_fact is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Food item has no nutrition facts: {food_item.name}",
            )

        return food_item

    @staticmethod
    def _scale_nutrient(per_100g: float, grams: float) -> float:
        return round((grams / 100.0) * per_100g, 2)

    def create_recipe(
        self,
        current_user: User,
        payload: RecipeCreateRequest,
    ) -> Recipe:
        recipe = Recipe(
            created_by_user_id=current_user.id,
            name=payload.name.strip(),
            slug=self._generate_unique_slug(payload.name),
            description=payload.description.strip() if payload.description else None,
            instructions=payload.instructions.strip() if payload.instructions else None,
            prep_time_minutes=payload.prep_time_minutes,
            cook_time_minutes=payload.cook_time_minutes,
            servings=payload.servings,
            category=payload.category.strip() if payload.category else None,
            diet_type=payload.diet_type.strip() if payload.diet_type else None,
            source=payload.source.strip().lower(),
            is_active=True,
            total_calories=0,
            total_protein_g=0,
            total_carbs_g=0,
            total_fat_g=0,
        )

        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for index, ingredient_payload in enumerate(payload.ingredients, start=1):
            food_item = self._get_food_item_with_nutrition(ingredient_payload.food_item_id)
            nutrition = food_item.nutrition_fact
            assert nutrition is not None

            grams = round(ingredient_payload.grams, 2)

            ingredient = RecipeIngredient(
                food_item_id=food_item.id,
                position=index,
                ingredient_name_snapshot=food_item.name,
                quantity_label=(
                    ingredient_payload.quantity_label.strip()
                    if ingredient_payload.quantity_label
                    else None
                ),
                grams=grams,
                notes=ingredient_payload.notes.strip() if ingredient_payload.notes else None,
            )
            recipe.ingredients.append(ingredient)

            total_calories += self._scale_nutrient(nutrition.calories_per_100g, grams)
            total_protein += self._scale_nutrient(nutrition.protein_g_per_100g, grams)
            total_carbs += self._scale_nutrient(nutrition.carbs_g_per_100g, grams)
            total_fat += self._scale_nutrient(nutrition.fat_g_per_100g, grams)

        recipe.total_calories = round(total_calories, 2)
        recipe.total_protein_g = round(total_protein, 2)
        recipe.total_carbs_g = round(total_carbs, 2)
        recipe.total_fat_g = round(total_fat, 2)

        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)

        return self.get_recipe(recipe.id)

    def list_recipes(
        self,
        query: str | None = None,
        category: str | None = None,
        diet_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Recipe]:
        statement: Select[tuple[Recipe]] = (
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
                (Recipe.name.ilike(pattern))
                | (Recipe.description.ilike(pattern))
                | (Recipe.category.ilike(pattern))
            )

        return list(self.db.scalars(statement).all())

    def get_recipe(self, recipe_id: str) -> Recipe:
        statement = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .where(
                Recipe.id == recipe_id,
                Recipe.is_active.is_(True),
            )
        )
        recipe = self.db.scalar(statement)

        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found.",
            )

        return recipe