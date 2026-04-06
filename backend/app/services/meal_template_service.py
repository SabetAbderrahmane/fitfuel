from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.meal_template import MealTemplate
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.meal_template import MealTemplateCreateRequest


class MealTemplateService:
    """
    Handles reusable meal template creation and lookup.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = re.sub(r"-{2,}", "-", value)
        return value.strip("-") or "meal-template"

    def _generate_unique_slug(self, name: str) -> str:
        base = self._slugify(name)
        slug = base
        counter = 2

        while self.db.scalar(select(MealTemplate).where(MealTemplate.slug == slug)) is not None:
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    def _get_recipe(self, recipe_id: str) -> Recipe:
        recipe = self.db.scalar(
            select(Recipe).where(
                Recipe.id == recipe_id,
                Recipe.is_active.is_(True),
            )
        )

        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found.",
            )

        return recipe

    def create_template(
        self,
        current_user: User,
        payload: MealTemplateCreateRequest,
    ) -> MealTemplate:
        recipe = None
        if payload.recipe_id:
            recipe = self._get_recipe(payload.recipe_id)

        name = payload.name.strip() if payload.name else None
        if recipe and not name:
            name = recipe.name

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template name is required when recipe_id is not provided.",
            )

        estimated_calories = payload.estimated_calories
        estimated_protein_g = payload.estimated_protein_g
        estimated_carbs_g = payload.estimated_carbs_g
        estimated_fat_g = payload.estimated_fat_g

        category = payload.category.strip() if payload.category else None
        diet_type = payload.diet_type.strip() if payload.diet_type else None
        description = payload.description.strip() if payload.description else None

        if recipe is not None:
            if estimated_calories is None:
                estimated_calories = recipe.total_calories
            if estimated_protein_g is None:
                estimated_protein_g = recipe.total_protein_g
            if estimated_carbs_g is None:
                estimated_carbs_g = recipe.total_carbs_g
            if estimated_fat_g is None:
                estimated_fat_g = recipe.total_fat_g
            if category is None:
                category = recipe.category
            if diet_type is None:
                diet_type = recipe.diet_type
            if description is None:
                description = recipe.description

        template = MealTemplate(
            created_by_user_id=current_user.id,
            recipe_id=recipe.id if recipe else None,
            name=name,
            slug=self._generate_unique_slug(name),
            meal_slot=payload.meal_slot,
            category=category,
            diet_type=diet_type,
            source=payload.source.strip().lower(),
            description=description,
            notes=payload.notes.strip() if payload.notes else None,
            estimated_calories=estimated_calories,
            estimated_protein_g=estimated_protein_g,
            estimated_carbs_g=estimated_carbs_g,
            estimated_fat_g=estimated_fat_g,
            is_active=True,
        )

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        return template

    def list_templates(
        self,
        query: str | None = None,
        meal_slot: str | None = None,
        category: str | None = None,
        diet_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MealTemplate]:
        statement: Select[tuple[MealTemplate]] = (
            select(MealTemplate)
            .where(MealTemplate.is_active.is_(True))
            .order_by(MealTemplate.name.asc())
            .offset(offset)
            .limit(limit)
        )

        if meal_slot:
            statement = statement.where(
                func.lower(MealTemplate.meal_slot) == meal_slot.strip().lower()
            )

        if category:
            statement = statement.where(
                func.lower(MealTemplate.category) == category.strip().lower()
            )

        if diet_type:
            statement = statement.where(
                func.lower(MealTemplate.diet_type) == diet_type.strip().lower()
            )

        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                (MealTemplate.name.ilike(pattern))
                | (MealTemplate.description.ilike(pattern))
                | (MealTemplate.category.ilike(pattern))
            )

        return list(self.db.scalars(statement).all())

    def get_template(self, template_id: str) -> MealTemplate:
        template = self.db.scalar(
            select(MealTemplate).where(
                MealTemplate.id == template_id,
                MealTemplate.is_active.is_(True),
            )
        )

        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal template not found.",
            )

        return template