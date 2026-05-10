from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.food_item import FoodItem
from app.models.meal_template import MealTemplate
from app.models.nutrition_fact import NutritionFact
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.meal_plan import MealPlanGenerateRequest
from app.services.meal_plan_service import MealPlanService


SOURCE = "meal_plan_target_smoke"
EMAIL = "meal-plan-target-smoke@example.com"
USERNAME = "meal_plan_target_smoke"


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")


def _get_or_create_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == EMAIL))
    if user is not None:
        return user

    user = User(
        email=EMAIL,
        username=USERNAME,
        hashed_password="not-used-by-smoke-test",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()
    return user


def _ensure_profile(db: Session, user: User) -> None:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if profile is not None:
        return
    db.add(
        UserProfile(
            user_id=user.id,
            first_name="Meal Plan Smoke",
            age=30,
            sex="female",
            height_cm=170,
            current_weight_kg=70,
        )
    )


def _ensure_goal(db: Session, user: User) -> UserGoal:
    for goal in db.scalars(
        select(UserGoal).where(UserGoal.user_id == user.id, UserGoal.is_active.is_(True))
    ):
        goal.is_active = False

    goal = UserGoal(
        user_id=user.id,
        goal_type="maintain",
        calculation_mode="manual",
        target_calories=3500,
        target_protein_g=210,
        target_carbs_g=385,
        target_fat_g=105,
        is_active=True,
        notes="Smoke test high-calorie target.",
    )
    db.add(goal)
    db.flush()
    return goal


def _ensure_food(db: Session) -> FoodItem:
    slug = "smoke-target-bowl-base"
    food = db.scalar(select(FoodItem).where(FoodItem.slug == slug))
    if food is None:
        food = FoodItem(
            name="Smoke Target Bowl Base",
            slug=slug,
            category="mixed_meal",
            description="Synthetic smoke-test food for meal-plan target validation.",
            default_serving_size_g=100,
            default_serving_label="100 g",
            source=SOURCE,
            normalized_name="smoke target bowl base",
            display_name="Smoke Target Bowl Base",
            search_name="smoke target bowl base",
            is_active=True,
        )
        db.add(food)
        db.flush()
    food.is_active = True
    if food.nutrition_fact is None:
        food.nutrition_fact = NutritionFact(
            calories_per_100g=300,
            protein_g_per_100g=20,
            carbs_g_per_100g=35,
            fat_g_per_100g=9,
            source_quality="smoke_test",
        )
    else:
        food.nutrition_fact.calories_per_100g = 300
        food.nutrition_fact.protein_g_per_100g = 20
        food.nutrition_fact.carbs_g_per_100g = 35
        food.nutrition_fact.fat_g_per_100g = 9
    return food


def _ensure_template(db: Session, food: FoodItem, meal_slot: str) -> MealTemplate:
    name = f"Smoke Target {meal_slot.title()}"
    recipe_slug = _slug(f"{name} Recipe")
    recipe = db.scalar(select(Recipe).where(Recipe.slug == recipe_slug))
    if recipe is None:
        recipe = Recipe(
            name=f"{name} Recipe",
            slug=recipe_slug,
            description="Smoke-test recipe for target-aware meal generation.",
            instructions="Assemble and serve.",
            servings=1,
            category=meal_slot,
            diet_type="general",
            diet_tags_json={},
            allergen_flags_json={},
            source=SOURCE,
            is_active=True,
            total_calories=600,
            total_protein_g=40,
            total_carbs_g=70,
            total_fat_g=18,
        )
        db.add(recipe)
        db.flush()
    recipe.is_active = True

    ingredient = db.scalar(
        select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe.id,
            RecipeIngredient.food_item_id == food.id,
        )
    )
    if ingredient is None:
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                food_item_id=food.id,
                position=1,
                ingredient_name_snapshot=food.name,
                quantity_label="200 g",
                grams=200,
            )
        )
    else:
        ingredient.grams = 200
        ingredient.quantity_label = "200 g"

    template_slug = _slug(f"{name} Template")
    template = db.scalar(select(MealTemplate).where(MealTemplate.slug == template_slug))
    if template is None:
        template = MealTemplate(
            recipe_id=recipe.id,
            name=name,
            slug=template_slug,
            meal_slot=meal_slot,
            category=meal_slot,
            diet_type="general",
            diet_tags_json={},
            allergen_flags_json={},
            source=SOURCE,
            estimated_calories=600,
            estimated_protein_g=40,
            estimated_carbs_g=70,
            estimated_fat_g=18,
            is_active=True,
        )
        db.add(template)
    else:
        template.recipe_id = recipe.id
        template.meal_slot = meal_slot
        template.is_active = True
        template.estimated_calories = 600
        template.estimated_protein_g = 40
        template.estimated_carbs_g = 70
        template.estimated_fat_g = 18
    return template


def main() -> None:
    db = SessionLocal()
    try:
        user = _get_or_create_user(db)
        _ensure_profile(db, user)
        goal = _ensure_goal(db, user)
        food = _ensure_food(db)
        for slot in ["breakfast", "lunch", "dinner", "snack"]:
            _ensure_template(db, food, slot)
        db.commit()
        db.refresh(user)

        plan = MealPlanService(db).generate_meal_plan(
            user,
            MealPlanGenerateRequest(
                plan_date=date.today(),
                meal_slots=["breakfast", "lunch", "dinner", "snack"],
                max_items_per_slot=1,
                notes="Smoke test target-aware generated plan.",
            ),
        )

        delta = round(plan.total_calories - float(goal.target_calories), 2)
        delta_percent = round((delta / float(goal.target_calories)) * 100.0, 2)

        print("Meal plan target smoke test")
        print(f"target_calories: {goal.target_calories}")
        print(f"actual_calories: {plan.total_calories}")
        print(f"delta_percent: {delta_percent}%")
        print(
            "target_macros: "
            f"protein={goal.target_protein_g}g carbs={goal.target_carbs_g}g fat={goal.target_fat_g}g"
        )
        print(
            "actual_macros: "
            f"protein={plan.total_protein_g}g carbs={plan.total_carbs_g}g fat={plan.total_fat_g}g"
        )
        print("items:")
        for item in plan.items:
            print(
                f"- {item.meal_slot}: {item.food_name_snapshot} "
                f"{item.planned_grams}g {item.calories} kcal | {item.notes}"
            )

        if abs(delta_percent) > 15:
            raise SystemExit(
                "Generated plan is outside +/-15% of the calorie target. "
                "Inspect available templates and scaling notes."
            )
        print("status: within +/-15% calorie target")
    finally:
        db.close()


if __name__ == "__main__":
    main()
