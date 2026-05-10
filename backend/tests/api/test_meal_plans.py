from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.allergy import Allergy
from app.models.dietary_preference import DietaryPreference
from app.models.food_alias import FoodAlias
from app.models.food_item import FoodItem
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.meal_template import MealTemplate
from app.models.nutrition_fact import NutritionFact
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile


def add_profile(db: Session, user: User) -> UserProfile:
    profile = UserProfile(
        user_id=user.id,
        first_name="Meal",
        age=30,
        sex="female",
        height_cm=170,
        current_weight_kg=70,
    )
    db.add(profile)
    db.commit()
    return profile


def add_goal(
    db: Session,
    user: User,
    *,
    calories: float = 2000,
    protein: float = 130,
    carbs: float = 220,
    fat: float = 60,
) -> UserGoal:
    goal = UserGoal(
        user_id=user.id,
        goal_type="maintain",
        target_calories=calories,
        target_protein_g=protein,
        target_carbs_g=carbs,
        target_fat_g=fat,
        is_active=True,
    )
    db.add(goal)
    db.commit()
    return goal


def add_food(
    db: Session,
    name: str,
    *,
    calories: float = 180,
    protein: float = 25,
    carbs: float = 5,
    fat: float = 4,
    category: str = "protein",
    description: str = "",
    usage_count: int = 0,
    popularity_score: float = 0,
    aliases: list[str] | None = None,
) -> FoodItem:
    slug = name.lower().replace(" ", "-")
    food = FoodItem(
        name=name,
        slug=slug,
        category=category,
        description=description,
        default_serving_size_g=100,
        source="manual",
        normalized_name=name.lower(),
        display_name=name,
        search_name=name.lower(),
        usage_count=usage_count,
        popularity_score=popularity_score,
        is_active=True,
    )
    food.nutrition_fact = NutritionFact(
        calories_per_100g=calories,
        protein_g_per_100g=protein,
        carbs_g_per_100g=carbs,
        fat_g_per_100g=fat,
    )
    for alias in aliases or []:
        food.aliases.append(
            FoodAlias(
                alias_text=alias,
                normalized_alias=alias.lower(),
                alias_type="synonym",
            )
        )
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


def add_recipe_template(
    db: Session,
    title: str,
    *,
    meal_slot: str = "lunch",
    ingredients: list[FoodItem],
    grams: list[float] | None = None,
    diet_tags: dict | None = None,
    allergen_flags: dict | None = None,
    estimated_calories: float | None = None,
    estimated_protein_g: float | None = None,
    estimated_carbs_g: float | None = None,
    estimated_fat_g: float | None = None,
) -> MealTemplate:
    suffix = uuid4().hex[:8]
    recipe = Recipe(
        name=title,
        slug=f"{title.lower().replace(' ', '-')}-{suffix}",
        description="Imported from RecipeNLG for thesis/demo use only.",
        instructions="Cook and serve.",
        servings=1,
        category=meal_slot,
        diet_type="general",
        diet_tags_json=diet_tags or {},
        allergen_flags_json=allergen_flags or {},
        source="recipenlg_thesis",
        is_active=True,
        total_calories=estimated_calories or 500,
        total_protein_g=estimated_protein_g or 35,
        total_carbs_g=estimated_carbs_g or 45,
        total_fat_g=estimated_fat_g or 15,
    )
    db.add(recipe)
    db.flush()

    grams = grams or [100.0 for _ in ingredients]
    for position, (food, ingredient_grams) in enumerate(zip(ingredients, grams), start=1):
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                food_item_id=food.id,
                position=position,
                ingredient_name_snapshot=food.name,
                quantity_label=f"{ingredient_grams}g",
                grams=ingredient_grams,
            )
        )

    template = MealTemplate(
        recipe_id=recipe.id,
        name=title,
        slug=f"{recipe.slug}-template",
        meal_slot=meal_slot,
        category=meal_slot,
        diet_type="general",
        diet_tags_json=diet_tags or {},
        allergen_flags_json=allergen_flags or {},
        source="recipenlg_thesis",
        estimated_calories=estimated_calories or 500,
        estimated_protein_g=estimated_protein_g or 35,
        estimated_carbs_g=estimated_carbs_g or 45,
        estimated_fat_g=estimated_fat_g or 15,
        is_active=True,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def generate_payload(**overrides):
    payload = {
        "plan_date": date(2026, 5, 8).isoformat(),
        "meal_slots": ["lunch"],
        "preferred_food_item_ids": [],
        "max_items_per_slot": 1,
        "notes": "test generated plan",
    }
    payload.update(overrides)
    return payload


def test_generate_endpoint_uses_existing_service_method_without_attribute_error(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Grilled Chicken", usage_count=20, popularity_score=3)

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["generation_mode"] == "rule_based"


def test_successful_generated_meal_plan_persists_plan_and_items(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    food = add_food(db_session, "Grilled Chicken")

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    persisted_plan = db_session.scalar(select(MealPlan).where(MealPlan.id == body["id"]))
    persisted_items = db_session.scalars(
        select(MealPlanItem).where(MealPlanItem.meal_plan_id == body["id"])
    ).all()
    assert persisted_plan is not None
    assert len(persisted_items) == 1
    assert persisted_items[0].food_item_id == food.id
    assert persisted_items[0].food_name_snapshot == "Grilled Chicken"
    assert persisted_items[0].calories > 0


def test_template_based_generation_succeeds_when_templates_exist(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    chicken = add_food(db_session, "Template Chicken", calories=180, protein=30)
    rice = add_food(db_session, "Template Rice", calories=130, protein=3, carbs=28, category="carb")
    add_recipe_template(
        db_session,
        "Chicken Rice Template",
        ingredients=[chicken, rice],
        grams=[150, 120],
        estimated_calories=520,
        estimated_protein_g=50,
        estimated_carbs_g=45,
        estimated_fat_g=10,
    )

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["generation_mode"] == "rule_based"
    assert body["item_count"] == 2
    assert all(item["notes"].startswith("From recipe: Chicken Rice Template") for item in body["items"])
    assert all("serving_multiplier=" in item["notes"] for item in body["items"])
    assert all(item["source_recipe_name"] == "Chicken Rice Template" for item in body["items"])
    assert all(item["source_template_name"] == "Chicken Rice Template" for item in body["items"])
    assert all(item["source_generation_type"] == "meal_template" for item in body["items"])
    assert body["grouped_meals"][0]["recipe_name"] == "Chicken Rice Template"
    assert len(body["grouped_meals"][0]["items"]) == 2
    assert body["total_calories"] == round(sum(item["calories"] for item in body["items"]), 2)


def test_template_generation_excludes_peanut_allergy(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    peanut = add_food(db_session, "Peanut Sauce", calories=590, protein=25, fat=50)
    turkey = add_food(db_session, "Safe Turkey", calories=160, protein=28)
    add_recipe_template(
        db_session,
        "Peanut Lunch",
        ingredients=[peanut],
        allergen_flags={"contains_peanut": True},
        estimated_calories=500,
    )
    add_recipe_template(
        db_session,
        "Safe Turkey Lunch",
        ingredients=[turkey],
        allergen_flags={"contains_peanut": False},
        estimated_calories=500,
    )
    db_session.add(Allergy(user_id=test_user.id, allergen_name="peanuts", is_active=True))
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_name_snapshot"] == "Safe Turkey"


def test_template_generation_excludes_dairy_restriction(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    cheese = add_food(db_session, "Cheese", calories=400, protein=25, fat=33, category="dairy")
    tofu = add_food(db_session, "Tofu Bowl", calories=140, protein=16, category="protein")
    add_recipe_template(
        db_session,
        "Cheese Lunch",
        ingredients=[cheese],
        allergen_flags={"contains_dairy": True},
        estimated_calories=520,
    )
    add_recipe_template(
        db_session,
        "Dairy Free Tofu Lunch",
        ingredients=[tofu],
        allergen_flags={"contains_dairy": False},
        diet_tags={"dairy_free_candidate": True},
        estimated_calories=520,
    )
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="restriction",
            value="dairy_free",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_name_snapshot"] == "Tofu Bowl"


def test_template_generation_requires_vegetarian_candidate(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    chicken = add_food(db_session, "Chicken Strip", calories=180, protein=30)
    lentils = add_food(db_session, "Lentils", calories=116, protein=9, carbs=20)
    add_recipe_template(
        db_session,
        "Chicken Lunch",
        ingredients=[chicken],
        diet_tags={"vegetarian_candidate": False},
        estimated_calories=510,
    )
    add_recipe_template(
        db_session,
        "Vegetarian Lentil Lunch",
        ingredients=[lentils],
        diet_tags={"vegetarian_candidate": True},
        estimated_calories=510,
    )
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="diet_type",
            value="vegetarian",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_name_snapshot"] == "Lentils"


def test_template_generation_halal_rejects_pork_or_alcohol(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    pork = add_food(db_session, "Pork", calories=240, protein=25, fat=14)
    salmon = add_food(db_session, "Halal Salmon", calories=200, protein=25, fat=10)
    add_recipe_template(
        db_session,
        "Pork Lunch",
        ingredients=[pork],
        diet_tags={"halal_candidate": True},
        allergen_flags={"contains_pork": True},
        estimated_calories=500,
    )
    add_recipe_template(
        db_session,
        "Halal Salmon Lunch",
        ingredients=[salmon],
        diet_tags={"halal_candidate": True},
        allergen_flags={"contains_pork": False, "contains_alcohol": False},
        estimated_calories=500,
    )
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="diet_type",
            value="halal",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_name_snapshot"] == "Halal Salmon"


def test_template_generation_disliked_food_excludes_recipe_template_or_ingredient(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    broccoli = add_food(db_session, "Broccoli", calories=55, protein=4, carbs=11)
    turkey = add_food(db_session, "Plain Turkey", calories=160, protein=28)
    add_recipe_template(db_session, "Broccoli Bowl", ingredients=[broccoli], estimated_calories=500)
    add_recipe_template(db_session, "Plain Turkey Bowl", ingredients=[turkey], estimated_calories=500)
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="disliked_food",
            value="broccoli",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_name_snapshot"] == "Plain Turkey"


def test_template_generation_persists_plan_and_items(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    salmon = add_food(db_session, "Template Salmon", calories=200, protein=25, fat=10)
    add_recipe_template(db_session, "Salmon Recipe", ingredients=[salmon], grams=[180])

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    persisted_plan = db_session.scalar(select(MealPlan).where(MealPlan.id == body["id"]))
    persisted_items = db_session.scalars(
        select(MealPlanItem).where(MealPlanItem.meal_plan_id == body["id"])
    ).all()
    assert persisted_plan is not None
    assert len(persisted_items) == 1
    assert persisted_items[0].notes.startswith("From recipe: Salmon Recipe")
    assert "serving_multiplier=" in persisted_items[0].notes
    assert persisted_items[0].source_recipe_name == "Salmon Recipe"
    assert persisted_items[0].source_template_name == "Salmon Recipe"
    assert persisted_items[0].source_generation_type == "meal_template"
    assert persisted_plan.total_calories == persisted_items[0].calories


def test_generation_falls_back_to_raw_food_when_no_template_available(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    raw_food = add_food(db_session, "Fallback Chicken")

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["items"][0]["food_item_id"] == raw_food.id
    assert body["items"][0]["source_generation_type"] == "raw_food_fallback"
    assert body["items"][0]["source_recipe_name"] is None
    assert body["items"][0]["source_template_name"] is None
    assert "Fallback raw-food generation used" in body["items"][0]["notes"]
    assert "Fallback raw-food generation used" in body["notes"]


def test_template_generated_response_includes_metadata_and_grouping(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    tofu = add_food(db_session, "Grouped Tofu", calories=140, protein=16)
    rice = add_food(db_session, "Grouped Rice", calories=130, protein=3, carbs=28)
    template = add_recipe_template(
        db_session,
        "Grouped Tofu Rice",
        ingredients=[tofu, rice],
        grams=[100, 100],
    )

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    assert {item["source_recipe_id"] for item in body["items"]} == {template.recipe_id}
    assert {item["source_template_id"] for item in body["items"]} == {template.id}
    assert body["grouped_meals"][0]["recipe_name"] == "Grouped Tofu Rice"
    assert body["grouped_meals"][0]["template_name"] == "Grouped Tofu Rice"
    assert body["grouped_meals"][0]["source_generation_type"] == "meal_template"
    assert len(body["grouped_meals"][0]["items"]) == 2


def test_generated_full_day_plan_targets_3000_calorie_goal(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user, calories=3000, protein=180, carbs=330, fat=90)
    dense_food = add_food(
        db_session,
        "Target Dense Bowl Base",
        calories=300,
        protein=20,
        carbs=35,
        fat=9,
    )
    for slot in ["breakfast", "lunch", "dinner", "snack"]:
        add_recipe_template(
            db_session,
            f"Target {slot.title()}",
            meal_slot=slot,
            ingredients=[dense_food],
            grams=[200],
            estimated_calories=600,
            estimated_protein_g=40,
            estimated_carbs_g=70,
            estimated_fat_g=18,
        )

    response = client.post(
        "/api/v1/meal-plans/generate",
        json=generate_payload(meal_slots=["breakfast", "lunch", "dinner", "snack"]),
    )

    assert response.status_code == 201
    body = response.json()
    assert 2550 <= body["total_calories"] <= 3450
    assert "target_status=within_target" in body["notes"]


def test_generated_high_calorie_plan_is_not_tiny_when_templates_exist(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user, calories=3500, protein=210, carbs=385, fat=105)
    dense_food = add_food(
        db_session,
        "High Target Bowl Base",
        calories=300,
        protein=20,
        carbs=35,
        fat=9,
    )
    for slot in ["breakfast", "lunch", "dinner", "snack"]:
        add_recipe_template(
            db_session,
            f"High Target {slot.title()}",
            meal_slot=slot,
            ingredients=[dense_food],
            grams=[200],
            estimated_calories=600,
            estimated_protein_g=40,
            estimated_carbs_g=70,
            estimated_fat_g=18,
        )

    response = client.post(
        "/api/v1/meal-plans/generate",
        json=generate_payload(meal_slots=["breakfast", "lunch", "dinner", "snack"]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_calories"] > 1500
    assert 2975 <= body["total_calories"] <= 4025


def test_recipe_ingredients_are_scaled_without_mutating_source_rows(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user, calories=2500)
    tofu = add_food(db_session, "Scaling Tofu", calories=200, protein=20)
    template = add_recipe_template(
        db_session,
        "Scaling Tofu Bowl",
        ingredients=[tofu],
        grams=[150],
        estimated_calories=300,
    )
    source_ingredient = db_session.scalar(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == template.recipe_id)
    )
    assert source_ingredient is not None
    original_grams = source_ingredient.grams

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    db_session.refresh(source_ingredient)
    body = response.json()
    assert source_ingredient.grams == original_grams
    assert body["items"][0]["planned_grams"] > original_grams
    assert "serving_multiplier=" in body["items"][0]["notes"]


def test_max_items_per_slot_does_not_truncate_recipe_ingredients(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    chicken = add_food(db_session, "Expansion Chicken", calories=180, protein=30)
    rice = add_food(db_session, "Expansion Rice", calories=130, protein=3, carbs=28, category="carb")
    beans = add_food(db_session, "Expansion Beans", calories=120, protein=9, carbs=21, category="protein")
    add_recipe_template(
        db_session,
        "Expansion Bowl",
        ingredients=[chicken, rice, beans],
        grams=[100, 100, 100],
    )

    response = client.post(
        "/api/v1/meal-plans/generate",
        json=generate_payload(max_items_per_slot=1),
    )

    assert response.status_code == 201
    assert response.json()["item_count"] == 3


def test_insufficient_templates_are_marked_when_plan_stays_below_target(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user, calories=3500)
    lean_food = add_food(db_session, "Tiny Lean Template Food", calories=80, protein=12)
    add_recipe_template(
        db_session,
        "Tiny Lean Lunch",
        ingredients=[lean_food],
        grams=[100],
        estimated_calories=80,
    )

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["total_calories"] < 2975
    assert "insufficient matching templates" in body["notes"]
    assert "target_status=below_target" in body["notes"]


def test_meal_plan_totals_equal_sum_of_generated_items(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user, calories=2800)
    salmon = add_food(db_session, "Totals Salmon", calories=206, protein=22, fat=12)
    rice = add_food(db_session, "Totals Rice", calories=130, protein=3, carbs=28, fat=0.3, category="carb")
    add_recipe_template(
        db_session,
        "Totals Dinner",
        meal_slot="dinner",
        ingredients=[salmon, rice],
        grams=[180, 220],
        estimated_calories=657,
    )

    response = client.post(
        "/api/v1/meal-plans/generate",
        json=generate_payload(meal_slots=["dinner"]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_calories"] == round(sum(item["calories"] for item in body["items"]), 2)
    assert body["total_protein_g"] == round(sum(item["protein_g"] for item in body["items"]), 2)
    assert body["total_carbs_g"] == round(sum(item["carbs_g"] for item in body["items"]), 2)
    assert body["total_fat_g"] == round(sum(item["fat_g"] for item in body["items"]), 2)


def test_repeated_generation_prefers_some_template_variety(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    chicken = add_food(db_session, "Variety Chicken", calories=180, protein=30)
    salmon = add_food(db_session, "Variety Salmon", calories=200, protein=25, fat=10)
    add_recipe_template(
        db_session,
        "Variety Chicken Bowl",
        ingredients=[chicken],
        estimated_calories=500,
        estimated_protein_g=45,
    )
    add_recipe_template(
        db_session,
        "Variety Salmon Bowl",
        ingredients=[salmon],
        estimated_calories=505,
        estimated_protein_g=44,
    )

    recipe_sets = []
    for _ in range(2):
        response = client.post("/api/v1/meal-plans/generate", json=generate_payload())
        assert response.status_code == 201
        recipe_sets.append(
            {
                item["source_recipe_name"]
                for item in response.json()["items"]
                if item["source_recipe_name"] is not None
            }
        )

    assert any(len(recipe_names) > 1 for recipe_names in recipe_sets)


def test_missing_profile_blocks_generation(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_goal(db_session, test_user)
    add_food(db_session, "Grilled Chicken")

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "User profile is required before generating a meal plan."


def test_missing_active_goal_blocks_generation(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_food(db_session, "Grilled Chicken")

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 404
    assert response.json()["detail"] == "No active goal found for this user."


def test_allergy_filtering_excludes_unsafe_food(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Peanut Chicken", aliases=["groundnut chicken"])
    safe_food = add_food(db_session, "Turkey Rice Bowl", usage_count=5)
    db_session.add(Allergy(user_id=test_user.id, allergen_name="peanut", is_active=True))
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    selected = response.json()["items"][0]
    assert selected["food_item_id"] == safe_food.id
    assert "Peanut" not in selected["food_name_snapshot"]


def test_disliked_food_filtering_excludes_disliked_food(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Broccoli Chicken Bowl", usage_count=50, popularity_score=5)
    safe_food = add_food(db_session, "Salmon Rice Bowl")
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="disliked_food",
            value="broccoli",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_item_id"] == safe_food.id


def test_preferred_food_gets_boosted_when_safe(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Grilled Chicken", usage_count=50, popularity_score=5)
    preferred = add_food(db_session, "Salmon Rice Bowl")
    db_session.add(
        DietaryPreference(
            user_id=test_user.id,
            preference_type="preferred_food",
            value="salmon",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    assert response.json()["items"][0]["food_item_id"] == preferred.id


def test_empty_usable_food_pool_returns_clear_error(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Food", calories=100, protein=5, carbs=10, fat=2)

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 400
    assert "No usable food items were available" in response.json()["detail"]


def test_generate_response_matches_meal_plan_response_shape(
    client: TestClient,
    db_session: Session,
    test_user: User,
):
    add_profile(db_session, test_user)
    add_goal(db_session, test_user)
    add_food(db_session, "Grilled Chicken")

    response = client.post("/api/v1/meal-plans/generate", json=generate_payload())

    assert response.status_code == 201
    body = response.json()
    assert {
        "id",
        "user_id",
        "goal_id",
        "plan_date",
        "generation_mode",
        "notes",
        "total_calories",
        "total_protein_g",
        "total_carbs_g",
        "total_fat_g",
        "item_count",
        "items",
        "grouped_meals",
        "created_at",
        "updated_at",
    } == set(body)
    assert {
        "id",
        "meal_plan_id",
        "food_item_id",
        "source_recipe_id",
        "source_recipe_name",
        "source_template_id",
        "source_template_name",
        "source_generation_type",
        "meal_slot",
        "position",
        "food_name_snapshot",
        "brand_snapshot",
        "planned_quantity",
        "planned_grams",
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "notes",
        "created_at",
        "updated_at",
    } == set(body["items"][0])
