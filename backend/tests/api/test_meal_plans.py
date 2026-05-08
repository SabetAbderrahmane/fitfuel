from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.allergy import Allergy
from app.models.dietary_preference import DietaryPreference
from app.models.food_alias import FoodAlias
from app.models.food_item import FoodItem
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.nutrition_fact import NutritionFact
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


def add_goal(db: Session, user: User) -> UserGoal:
    goal = UserGoal(
        user_id=user.id,
        goal_type="maintain",
        target_calories=2000,
        target_protein_g=130,
        target_carbs_g=220,
        target_fat_g=60,
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
        "created_at",
        "updated_at",
    } == set(body)
    assert {
        "id",
        "meal_plan_id",
        "food_item_id",
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
