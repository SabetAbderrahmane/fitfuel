from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@compiles(TSVECTOR, "sqlite")
def compile_tsvector_sqlite(*_args, **_kwargs) -> str:
    return "TEXT"


from app.api.routes.meal_plans import router as meal_plans_router  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.models.allergy import Allergy  # noqa: E402
from app.models.dietary_preference import DietaryPreference  # noqa: E402
from app.models.food_alias import FoodAlias  # noqa: E402
from app.models.food_item import FoodItem  # noqa: E402
from app.models.meal_plan import MealPlan  # noqa: E402
from app.models.meal_plan_item import MealPlanItem  # noqa: E402
from app.models.nutrition_fact import NutritionFact  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.user_goal import UserGoal  # noqa: E402
from app.models.user_profile import UserProfile  # noqa: E402
from app.services.auth_service import get_current_user  # noqa: E402


TEST_TABLES = [
    User.__table__,
    UserProfile.__table__,
    UserGoal.__table__,
    Allergy.__table__,
    DietaryPreference.__table__,
    FoodItem.__table__,
    FoodAlias.__table__,
    NutritionFact.__table__,
    MealPlan.__table__,
    MealPlanItem.__table__,
]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine, tables=TEST_TABLES)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine, tables=reversed(TEST_TABLES))
        engine.dispose()


@pytest.fixture()
def test_user(db_session: Session) -> User:
    user = User(
        email="meal-plan-user@example.com",
        username="meal_plan_user",
        hashed_password="not-used",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def client(db_session: Session, test_user: User) -> Generator[TestClient, None, None]:
    app = FastAPI()
    app.include_router(meal_plans_router, prefix="/api/v1/meal-plans")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
