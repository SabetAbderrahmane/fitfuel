from __future__ import annotations

from datetime import date
from typing import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes.food_logs import router as food_logs_router
from app.db.session import get_db
from app.models.food_item import FoodItem
from app.models.nutrition_fact import NutritionFact
from app.models.user import User
from app.schemas.food_log import FoodLogCreateRequest, FoodLogItemCreateRequest
from app.scripts.seed_cv_label_food_maps import DEMO_SOURCE, seed_cv_label_food_maps
from app.services.auth_service import get_current_user
from app.services.food_log_service import FoodLogService


def add_user(db: Session, email: str, username: str) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password="not-used",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_food(
    db: Session,
    name: str,
    *,
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    source: str = "manual",
) -> FoodItem:
    slug = f"{source}-{name.lower().replace(' ', '-')}"
    food = FoodItem(
        name=name,
        slug=slug,
        source=source,
        category="test",
        default_serving_size_g=100,
        default_serving_label="100 g",
        normalized_name=name.lower(),
        display_name=name,
        search_name=name.lower(),
        is_active=True,
    )
    food.nutrition_fact = NutritionFact(
        calories_per_100g=calories,
        protein_g_per_100g=protein,
        carbs_g_per_100g=carbs,
        fat_g_per_100g=fat,
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


def create_log(
    db: Session,
    user: User,
    food: FoodItem,
    *,
    logged_for_date: date,
    grams: float = 100,
) -> None:
    FoodLogService(db).create_food_log(
        current_user=user,
        payload=FoodLogCreateRequest(
            logged_for_date=logged_for_date,
            meal_type="lunch",
            items=[
                FoodLogItemCreateRequest(
                    food_item_id=food.id,
                    quantity=1,
                    grams=grams,
                )
            ],
        ),
    )


def test_creating_food_log_changes_daily_summary_totals(
    db_session: Session,
    test_user: User,
) -> None:
    caesar = add_food(
        db_session,
        "Caesar Salad",
        calories=180,
        protein=5,
        carbs=7,
        fat=15,
    )
    create_log(db_session, test_user, caesar, logged_for_date=date(2026, 5, 10))

    summary = FoodLogService(db_session).get_daily_summary(test_user, date(2026, 5, 10))

    assert summary.total_calories == 180
    assert summary.total_protein_g == 5
    assert summary.total_carbs_g == 7
    assert summary.total_fat_g == 15
    assert summary.log_count == 1


def test_daily_summary_filters_by_authenticated_user(
    db_session: Session,
    test_user: User,
) -> None:
    other_user = add_user(db_session, "other@example.com", "other_user")
    food = add_food(db_session, "Pizza", calories=266, protein=11, carbs=33, fat=10)
    create_log(db_session, test_user, food, logged_for_date=date(2026, 5, 10))
    create_log(db_session, other_user, food, logged_for_date=date(2026, 5, 10))

    summary = FoodLogService(db_session).get_daily_summary(test_user, date(2026, 5, 10))

    assert summary.total_calories == 266
    assert summary.log_count == 1


def test_daily_summary_filters_by_date(
    db_session: Session,
    test_user: User,
) -> None:
    food = add_food(db_session, "Ramen", calories=110, protein=4, carbs=15, fat=4)
    create_log(db_session, test_user, food, logged_for_date=date(2026, 5, 10))
    create_log(db_session, test_user, food, logged_for_date=date(2026, 5, 9))

    summary = FoodLogService(db_session).get_daily_summary(test_user, date(2026, 5, 10))

    assert summary.total_calories == 110
    assert summary.log_count == 1


def test_cv_demo_catalog_food_logs_contribute_calories_and_macros(
    db_session: Session,
    test_user: User,
) -> None:
    seed_cv_label_food_maps(db_session)
    sushi = (
        db_session.query(FoodItem)
        .filter(
            FoodItem.source == DEMO_SOURCE,
            FoodItem.normalized_name == "sushi",
        )
        .one()
    )
    create_log(db_session, test_user, sushi, logged_for_date=date(2026, 5, 10))

    summary = FoodLogService(db_session).get_daily_summary(test_user, date(2026, 5, 10))

    assert summary.total_calories == 145
    assert summary.total_protein_g == 6
    assert summary.total_carbs_g == 28
    assert summary.total_fat_g == 1


def test_daily_summary_endpoint_returns_authenticated_users_date_totals(
    db_session: Session,
    test_user: User,
) -> None:
    food = add_food(db_session, "Apple Pie", calories=237, protein=2.4, carbs=34, fat=11)
    create_log(db_session, test_user, food, logged_for_date=date(2026, 5, 10))

    app = FastAPI()
    app.include_router(food_logs_router, prefix="/api/v1/food-logs")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        response = client.get("/api/v1/food-logs/daily-summary?date=2026-05-10")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "date": "2026-05-10",
        "total_calories": 237.0,
        "total_protein_g": 2.4,
        "total_carbs_g": 34.0,
        "total_fat_g": 11.0,
        "log_count": 1,
    }
