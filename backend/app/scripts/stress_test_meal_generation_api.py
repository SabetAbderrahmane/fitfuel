from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timezone
from typing import Any

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.main import app
from app.models.allergy import Allergy
from app.models.dietary_preference import DietaryPreference
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile


EMAIL = "template-stress-user@fitfuel.local"
USERNAME = "template_stress_user"
PASSWORD = "TestPassword123!"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
PLAN_PAYLOAD = {
    "plan_date": "2026-05-10",
    "meal_slots": ["breakfast", "lunch", "dinner", "snack"],
    "preferred_food_item_ids": [],
    "max_items_per_slot": 1,
    "notes": "template-first backend stress test",
}

SCENARIOS = {
    "normal": {"allergies": [], "preferences": []},
    "peanut_allergy": {"allergies": ["peanut"], "preferences": []},
    "dairy_free": {"allergies": [], "preferences": [("restriction", "dairy_free")]},
    "vegetarian": {"allergies": [], "preferences": [("diet_type", "vegetarian")]},
    "halal": {"allergies": [], "preferences": [("diet_type", "halal")]},
}


class ApiHarness:
    def __init__(self, base_url: str, prefer_http: bool) -> None:
        self.base_url = base_url.rstrip("/")
        self.prefer_http = prefer_http
        self.mode = "http"
        self._client: httpx.Client | TestClient
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)
        if not prefer_http or not self._http_server_available():
            self.mode = "testclient"
            self._client.close()
            self._client = TestClient(app, raise_server_exceptions=False)

    def _http_server_available(self) -> bool:
        try:
            response = self._client.get("/")
            return response.status_code < 500
        except httpx.HTTPError:
            return False

    def close(self) -> None:
        self._client.close()

    def login(self) -> str:
        response = self._client.post(
            "/api/v1/auth/login",
            data={"username": EMAIL, "password": PASSWORD},
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        self._client.headers.update({"Authorization": f"Bearer {token}"})
        return token

    def get_current_user(self) -> dict[str, Any]:
        response = self._client.get("/api/v1/users/me")
        if response.status_code == 404:
            response = self._client.get("/api/v1/auth/me")
        if response.status_code >= 400:
            return {
                "endpoint_error": response.status_code,
                "body": response.text[:500],
            }
        return response.json()

    def generate_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._client.post("/api/v1/meal-plans/generate", json=payload)
        response.raise_for_status()
        return response.json()

    def list_plans(self) -> list[dict[str, Any]]:
        response = self._client.get("/api/v1/meal-plans")
        response.raise_for_status()
        return response.json()

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        response = self._client.get(f"/api/v1/meal-plans/{plan_id}")
        response.raise_for_status()
        return response.json()


def ensure_schema_ready() -> None:
    with SessionLocal() as db:
        columns = {column["name"] for column in inspect(db.bind).get_columns("meal_plan_items")}
        missing = {
            "source_recipe_id",
            "source_recipe_name",
            "source_template_id",
            "source_template_name",
            "source_generation_type",
        } - columns
        if missing:
            raise RuntimeError(
                "meal_plan_items source metadata columns are missing. "
                "Run `alembic upgrade head` before this stress test. "
                f"Missing: {', '.join(sorted(missing))}"
            )


def ensure_test_user() -> None:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == EMAIL))
        if user is None:
            user = User(
                email=EMAIL,
                username=USERNAME,
                hashed_password=get_password_hash(PASSWORD),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.flush()
        else:
            user.username = USERNAME
            user.hashed_password = get_password_hash(PASSWORD)
            user.is_active = True
            user.is_verified = True

        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
        if profile is None:
            db.add(
                UserProfile(
                    user_id=user.id,
                    first_name="Template",
                    last_name="Stress",
                    age=30,
                    sex="female",
                    height_cm=170,
                    start_weight_kg=70,
                    current_weight_kg=70,
                )
            )

        active_goals = db.scalars(
            select(UserGoal).where(UserGoal.user_id == user.id, UserGoal.is_active.is_(True))
        ).all()
        for goal in active_goals:
            goal.is_active = False
            goal.ended_at = datetime.now(timezone.utc)

        db.add(
            UserGoal(
                user_id=user.id,
                goal_type="maintain",
                calculation_mode="manual",
                target_calories=2000,
                target_protein_g=130,
                target_carbs_g=220,
                target_fat_g=60,
                is_active=True,
                started_at=datetime.now(timezone.utc),
                notes="Deterministic meal generation stress-test goal.",
            )
        )
        db.commit()


def configure_scenario(name: str) -> None:
    scenario = SCENARIOS[name]
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == EMAIL))
        if user is None:
            raise RuntimeError("Stress user was not created.")

        for allergy in db.scalars(select(Allergy).where(Allergy.user_id == user.id)).all():
            allergy.is_active = False
        for preference in db.scalars(
            select(DietaryPreference).where(DietaryPreference.user_id == user.id)
        ).all():
            preference.is_active = False

        for allergen in scenario["allergies"]:
            db.add(
                Allergy(
                    user_id=user.id,
                    allergen_name=allergen,
                    severity="test",
                    notes=f"Stress-test scenario: {name}",
                    is_active=True,
                )
            )
        for preference_type, value in scenario["preferences"]:
            db.add(
                DietaryPreference(
                    user_id=user.id,
                    preference_type=preference_type,
                    value=value,
                    notes=f"Stress-test scenario: {name}",
                    is_active=True,
                )
            )
        db.commit()


def extract_recipe_names(plan: dict[str, Any]) -> list[str]:
    names = []
    for item in plan.get("items", []):
        name = item.get("source_recipe_name")
        if not name and item.get("notes", "").startswith("From recipe: "):
            name = item["notes"].replace("From recipe: ", "", 1)
        if name:
            names.append(name)
    return names


def print_plan(plan: dict[str, Any], label: str) -> dict[str, Any]:
    recipe_names = extract_recipe_names(plan)
    fallback_used = any(
        item.get("source_generation_type") == "raw_food_fallback"
        or "Fallback raw-food generation used" in (item.get("notes") or "")
        for item in plan.get("items", [])
    )
    from_recipe_count = sum("From recipe:" in (item.get("notes") or "") for item in plan.get("items", []))

    print(f"\n=== {label} ===")
    print(f"plan id: {plan['id']}")
    print(f"generation_mode: {plan['generation_mode']}")
    print(
        "totals: "
        f"{plan['total_calories']} kcal, "
        f"P {plan['total_protein_g']}g, "
        f"C {plan['total_carbs_g']}g, "
        f"F {plan['total_fat_g']}g"
    )
    print(f"item_count: {plan['item_count']}")
    print(f"items with 'From recipe:': {from_recipe_count}/{len(plan.get('items', []))}")
    print(f"unique recipe names: {sorted(set(recipe_names)) or 'NONE'}")
    print(f"fallback raw-food generation used: {fallback_used}")
    print(f"grouped_meals present: {bool(plan.get('grouped_meals'))}")

    for item in plan.get("items", []):
        print(
            "- "
            f"{item['meal_slot']} | {item['food_name_snapshot']} | "
            f"{item['calories']} kcal | "
            f"P {item['protein_g']} C {item['carbs_g']} F {item['fat_g']} | "
            f"recipe={item.get('source_recipe_name')} | "
            f"template={item.get('source_template_name')} | "
            f"type={item.get('source_generation_type')} | "
            f"notes={item.get('notes')}"
        )

    return {
        "plan_id": plan["id"],
        "recipe_names": recipe_names,
        "food_names": [item["food_name_snapshot"] for item in plan.get("items", [])],
        "fallback_used": fallback_used,
    }


def response_shape_audit(plan: dict[str, Any]) -> None:
    item = plan["items"][0] if plan.get("items") else {}
    print("\n=== Response shape audit ===")
    print(f"item exposes recipe_id/source_recipe_id: {'source_recipe_id' in item}")
    print(f"item exposes recipe_name/source_recipe_name: {'source_recipe_name' in item}")
    print(f"item exposes meal_template_id/source_template_id: {'source_template_id' in item}")
    print(f"item exposes meal_template_name/source_template_name: {'source_template_name' in item}")
    print(f"response exposes grouped meal object: {'grouped_meals' in plan}")
    print(f"response still exposes flat MealPlanItem rows: {'items' in plan}")


def swagger_steps(base_url: str) -> None:
    print("\n=== Swagger UI manual steps ===")
    print(f"1. Open {base_url.rstrip('/')}/docs")
    print("2. Run POST /api/v1/auth/login with OAuth2 form data:")
    print(f"   username={EMAIL}")
    print(f"   password={PASSWORD}")
    print("3. Click Authorize and paste the returned access token as Bearer auth.")
    print("4. Run GET /api/v1/users/me to confirm the stress user.")
    print("5. Run POST /api/v1/meal-plans/generate with:")
    print(json.dumps(PLAN_PAYLOAD, indent=2))
    print("6. Inspect each item for source_recipe_name/source_template_name/source_generation_type.")
    print("7. Run GET /api/v1/meal-plans and GET /api/v1/meal-plans/{id} for the generated id.")


def curl_steps(base_url: str) -> None:
    base = base_url.rstrip("/")
    print("\n=== HTTP/curl steps ===")
    print(
        "TOKEN=$(curl -s -X POST "
        f"{base}/api/v1/auth/login "
        "-H \"Content-Type: application/x-www-form-urlencoded\" "
        f"-d \"username={EMAIL}&password={PASSWORD}\" | python -c "
        "\"import sys,json; print(json.load(sys.stdin)['access_token'])\")"
    )
    print(f"curl -s {base}/api/v1/users/me -H \"Authorization: Bearer $TOKEN\"")
    print(
        f"curl -s -X POST {base}/api/v1/meal-plans/generate "
        "-H \"Authorization: Bearer $TOKEN\" "
        "-H \"Content-Type: application/json\" "
        f"-d '{json.dumps(PLAN_PAYLOAD)}'"
    )


def run(args: argparse.Namespace) -> None:
    ensure_schema_ready()
    ensure_test_user()
    harness = ApiHarness(args.base_url, prefer_http=not args.force_testclient)
    print(f"API mode: {harness.mode}")
    try:
        harness.login()
        user = harness.get_current_user()
        if "endpoint_error" in user:
            print(
                "GET current-user endpoint failed during audit: "
                f"{user['endpoint_error']} {user['body']}"
            )
            print(f"Authenticated login still succeeded for {EMAIL}.")
        else:
            print(f"Authenticated user: {user.get('email')} ({user.get('username')})")

        repeated_results = []
        configure_scenario("normal")
        for index in range(1, 4):
            plan = harness.generate_plan(PLAN_PAYLOAD)
            repeated_results.append(print_plan(plan, f"normal repeated generation #{index}"))
            fetched = harness.get_plan(plan["id"])
            print(f"GET /meal-plans/{{id}} item_count: {fetched['item_count']}")
            if index == 1:
                response_shape_audit(plan)

        recipe_counter = Counter(name for result in repeated_results for name in result["recipe_names"])
        food_counter = Counter(name for result in repeated_results for name in result["food_names"])
        print("\n=== Repeated generation comparison ===")
        print(f"recipe names repeated: {dict(recipe_counter)}")
        print(f"food_name_snapshot repeated: {dict(food_counter)}")
        print(f"unique recipe count across 3 runs: {len(recipe_counter)}")
        print(f"unique food snapshot count across 3 runs: {len(food_counter)}")

        plans = harness.list_plans()
        print(f"GET /api/v1/meal-plans returned {len(plans)} plan(s).")

        for scenario_name in ("peanut_allergy", "dairy_free", "vegetarian", "halal"):
            configure_scenario(scenario_name)
            plan = harness.generate_plan({**PLAN_PAYLOAD, "notes": f"{PLAN_PAYLOAD['notes']} - {scenario_name}"})
            result = print_plan(plan, f"scenario: {scenario_name}")
            if result["fallback_used"]:
                print(f"WARNING: fallback used for {scenario_name}; inspect template coverage.")
    finally:
        configure_scenario("normal")
        harness.close()

    swagger_steps(args.base_url)
    curl_steps(args.base_url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stress-test meal generation API response shape and template use.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--force-testclient",
        action="store_true",
        help="Use FastAPI TestClient instead of HTTP, even if localhost is available.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
