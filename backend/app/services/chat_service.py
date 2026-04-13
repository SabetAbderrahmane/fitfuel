from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.food_item import FoodItem
from app.models.recipe import Recipe
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest


PLACEHOLDER_FOOD_NAMES = {
    "",
    "string",
    "test",
    "sample",
    "food",
    "item",
    "unknown",
}


SWAP_HINTS_BY_CATEGORY = {
    "carb": "Add more carb alternatives such as potatoes, oats, quinoa, pasta, or sweet potatoes.",
    "protein": "Add more protein alternatives such as tuna, tofu, yogurt, lean beef, or cottage cheese.",
    "fat": "Add more fat alternatives such as avocado, nuts, peanut butter, or olive oil.",
    "fruit": "Add more fruit alternatives such as banana, apple, berries, or orange.",
}


@dataclass(slots=True)
class FoodMatch:
    item: FoodItem
    score: float


class ChatService:
    """
    Deterministic meal assistant service.

    Improvements in this version:
    - exact food mention extraction before fuzzy matching
    - filtered food pool so placeholder/broken food rows do not pollute chat answers
    - more helpful swap suggestions when the catalog lacks a direct same-category alternative
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.goal_repository = GoalRepository(db)
        self.meal_plan_repository = MealPlanRepository(db)

    # -------------------------------------------------------------------------
    # General helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9\s]+", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @staticmethod
    def _is_reasonable_food_item(item: FoodItem) -> bool:
        if not item.is_active:
            return False

        name = (item.name or "").strip().lower()
        if name in PLACEHOLDER_FOOD_NAMES:
            return False

        if item.nutrition_fact is None:
            return False

        nutrition = item.nutrition_fact
        calories = float(nutrition.calories_per_100g)
        protein = float(nutrition.protein_g_per_100g)
        carbs = float(nutrition.carbs_g_per_100g)
        fat = float(nutrition.fat_g_per_100g)

        if calories < 0 or calories > 900:
            return False
        if protein < 0 or protein > 100:
            return False
        if carbs < 0 or carbs > 100:
            return False
        if fat < 0 or fat > 100:
            return False
        if protein + carbs + fat > 102:
            return False

        return True

    def _list_active_food_items(self) -> list[FoodItem]:
        items = list(
            self.db.scalars(
                select(FoodItem)
                .options(selectinload(FoodItem.nutrition_fact))
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.name.asc())
            ).all()
        )
        return [item for item in items if self._is_reasonable_food_item(item)]

    # -------------------------------------------------------------------------
    # Chat session CRUD
    # -------------------------------------------------------------------------

    def create_session(
        self,
        current_user: User,
        payload: ChatSessionCreateRequest,
    ) -> ChatSession:
        title = payload.title.strip() if payload.title else "New chat"

        session = ChatSession(
            user_id=current_user.id,
            title=title,
            status="active",
            summary=None,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def list_sessions(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ChatSession]:
        return self.chat_repository.list_sessions_for_user(
            current_user.id,
            limit=limit,
            offset=offset,
        )

    def get_session(
        self,
        current_user: User,
        chat_session_id: str,
    ) -> ChatSession:
        session = self.chat_repository.get_session_for_user(
            current_user.id,
            chat_session_id,
        )

        if session is None:
            raise ValueError("Chat session not found.")

        return session

    # -------------------------------------------------------------------------
    # Goal / meal summaries
    # -------------------------------------------------------------------------

    def _get_active_goal_summary(self, current_user: User) -> str:
        goal = self.goal_repository.get_active_for_user(current_user.id)
        if goal is None:
            return (
                "You do not have an active goal yet. "
                "Create a goal first so I can explain your calorie and macro targets."
            )

        return (
            f"Your current goal is **{goal.goal_type}**.\n\n"
            f"- Target calories: **{goal.target_calories} kcal/day**\n"
            f"- Protein: **{goal.target_protein_g} g/day**\n"
            f"- Carbs: **{goal.target_carbs_g} g/day**\n"
            f"- Fat: **{goal.target_fat_g} g/day**\n"
            f"- Calculation mode: **{goal.calculation_mode}**"
        )

    def _build_meal_plan_summary(self, current_user: User) -> str:
        plan = self.meal_plan_repository.get_latest_for_user(current_user.id)

        if plan is None:
            return "You do not have any meal plans yet."

        lines = [
            f"Your latest meal plan is for **{plan.plan_date}**.",
            "",
            f"- Total calories: **{plan.total_calories} kcal**",
            f"- Protein: **{plan.total_protein_g} g**",
            f"- Carbs: **{plan.total_carbs_g} g**",
            f"- Fat: **{plan.total_fat_g} g**",
            "",
            "Planned items:",
        ]

        for item in plan.items[:8]:
            lines.append(
                f"- **{item.meal_slot}**: {item.food_name_snapshot} ({item.planned_grams} g)"
            )

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Food suggestions
    # -------------------------------------------------------------------------

    def _list_top_protein_foods(self, limit: int = 5) -> list[FoodItem]:
        items = self._list_active_food_items()
        items.sort(
            key=lambda item: float(item.nutrition_fact.protein_g_per_100g) if item.nutrition_fact else 0.0,
            reverse=True,
        )
        return items[:limit]

    def _build_high_protein_suggestion(self) -> str:
        foods = self._list_top_protein_foods(limit=5)

        if not foods:
            return "I could not find any usable food catalog items with nutrition facts yet."

        lines = ["Here are some high-protein food options from your catalog:"]
        for food in foods:
            nutrition = food.nutrition_fact
            if nutrition is None:
                continue
            lines.append(
                f"- **{food.name}**: {nutrition.protein_g_per_100g} g protein / 100 g, "
                f"{nutrition.calories_per_100g} kcal / 100 g"
            )

        return "\n".join(lines)

    def _build_recipe_suggestion(self, content: str) -> str:
        pattern = f"%{content.strip()}%"
        recipes = list(
            self.db.scalars(
                select(Recipe)
                .options(selectinload(Recipe.ingredients))
                .where(
                    Recipe.is_active.is_(True),
                    or_(
                        Recipe.name.ilike(pattern),
                        Recipe.description.ilike(pattern),
                        Recipe.category.ilike(pattern),
                        Recipe.diet_type.ilike(pattern),
                    ),
                )
                .limit(3)
            ).all()
        )

        if not recipes:
            recipes = list(
                self.db.scalars(
                    select(Recipe)
                    .options(selectinload(Recipe.ingredients))
                    .where(Recipe.is_active.is_(True))
                    .order_by(Recipe.created_at.desc())
                    .limit(3)
                ).all()
            )

        if not recipes:
            return (
                "I could not find recipe records yet. "
                "Create recipes first and I will be able to recommend them here."
            )

        lines = ["Here are some recipe suggestions:"]
        for recipe in recipes:
            lines.append(
                f"- **{recipe.name}** — {recipe.total_calories} kcal total, "
                f"{recipe.total_protein_g} g protein total, servings: {recipe.servings}"
            )

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Swap logic
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_swap_target_phrase(content: str) -> str:
        lowered = content.strip().lower()

        patterns = [
            r"(?:swap|replace)\s+for\s+(?P<food>.+?)(?:[?.!]|$)",
            r"(?:swap|replace)\s+(?P<food>.+?)\s+(?:with|instead of|for)(?:\s+.+)?$",
            r"alternative\s+to\s+(?P<food>.+?)(?:[?.!]|$)",
            r"for\s+(?P<food>.+?)(?:[?.!]|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                value = match.group("food").strip()
                value = re.sub(r"\b(a|an|the|meal)\b", " ", value)
                value = re.sub(r"\s+", " ", value)
                return value.strip()

        return lowered

    def _find_best_matching_food(self, query_text: str) -> FoodItem | None:
        items = self._list_active_food_items()
        if not items:
            return None

        normalized_message = self._normalize_text(query_text)
        extracted_food_phrase = self._normalize_text(self._extract_swap_target_phrase(query_text))

        query_variants = [normalized_message]
        if extracted_food_phrase and extracted_food_phrase not in query_variants:
            query_variants.append(extracted_food_phrase)

        # Pass 1: exact or substring mention, preferring longer food names.
        items_by_name_length = sorted(
            items,
            key=lambda item: len(self._normalize_text(item.name)),
            reverse=True,
        )

        for variant in query_variants:
            for item in items_by_name_length:
                normalized_item_name = self._normalize_text(item.name)
                if normalized_item_name and normalized_item_name in variant:
                    return item

        # Pass 2: fuzzy match against the best extracted phrase.
        best_match: FoodMatch | None = None

        for item in items:
            normalized_item_name = self._normalize_text(item.name)

            for variant in query_variants:
                score = max(
                    float(fuzz.token_set_ratio(variant, normalized_item_name)),
                    float(fuzz.partial_ratio(variant, normalized_item_name)),
                    float(fuzz.ratio(variant, normalized_item_name)),
                )

                if best_match is None or score > best_match.score:
                    best_match = FoodMatch(item=item, score=score)

        if best_match is None or best_match.score < 45.0:
            return None

        return best_match.item

    @staticmethod
    def _swap_candidate_score(reference: FoodItem, candidate: FoodItem) -> float:
        if reference.nutrition_fact is None or candidate.nutrition_fact is None:
            return -9999.0

        ref = reference.nutrition_fact
        cand = candidate.nutrition_fact

        score = 0.0

        if (reference.category or "").strip().lower() == (candidate.category or "").strip().lower():
            score += 8.0

        score -= abs(float(ref.calories_per_100g) - float(cand.calories_per_100g)) / 40.0
        score -= abs(float(ref.protein_g_per_100g) - float(cand.protein_g_per_100g)) / 6.0
        score -= abs(float(ref.carbs_g_per_100g) - float(cand.carbs_g_per_100g)) / 6.0
        score -= abs(float(ref.fat_g_per_100g) - float(cand.fat_g_per_100g)) / 6.0

        return score

    def _build_swap_suggestion(self, content: str) -> str:
        referenced_food = self._find_best_matching_food(content)

        if referenced_food is None:
            return (
                "I could not confidently detect which food you want to swap. "
                "Try phrasing it like: `swap white rice for another carb` "
                "or `replace chicken breast with another protein`."
            )

        candidates = [
            item
            for item in self._list_active_food_items()
            if item.id != referenced_food.id and item.nutrition_fact is not None
        ]

        referenced_category = (referenced_food.category or "").strip().lower()
        same_category = [
            item
            for item in candidates
            if (item.category or "").strip().lower() == referenced_category
        ]

        if not same_category:
            hint = SWAP_HINTS_BY_CATEGORY.get(
                referenced_category,
                "Add more foods to your catalog so I can suggest stronger alternatives.",
            )
            return (
                f"I found **{referenced_food.name}**, but I do not have another active "
                f"**{referenced_category or 'similar'}** food in your catalog yet. {hint}"
            )

        ranked = sorted(
            same_category,
            key=lambda item: self._swap_candidate_score(referenced_food, item),
            reverse=True,
        )[:3]

        lines = [f"Possible swaps for **{referenced_food.name}**:"]
        for item in ranked:
            nutrition = item.nutrition_fact
            assert nutrition is not None
            lines.append(
                f"- **{item.name}**: {nutrition.calories_per_100g} kcal / 100 g, "
                f"{nutrition.protein_g_per_100g} g protein / 100 g, "
                f"{nutrition.carbs_g_per_100g} g carbs / 100 g, "
                f"{nutrition.fat_g_per_100g} g fat / 100 g"
            )

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Intent routing
    # -------------------------------------------------------------------------

    @staticmethod
    def _detect_intent(content: str) -> str:
        lowered = content.lower()

        if any(keyword in lowered for keyword in ["swap", "replace", "instead of", "alternative"]):
            return "meal_swap"

        if any(keyword in lowered for keyword in ["protein", "high protein"]):
            return "protein_suggestion"

        if any(keyword in lowered for keyword in ["recipe", "cook", "meal idea"]):
            return "recipe_suggestion"

        if any(keyword in lowered for keyword in ["meal plan", "plan today", "planned meals"]):
            return "meal_plan_summary"

        if any(keyword in lowered for keyword in ["goal", "calorie", "macro", "target"]):
            return "goal_summary"

        return "general_help"

    def _generate_assistant_response(
        self,
        current_user: User,
        content: str,
    ) -> tuple[str, str]:
        intent = self._detect_intent(content)

        if intent == "goal_summary":
            return intent, self._get_active_goal_summary(current_user)

        if intent == "protein_suggestion":
            return intent, self._build_high_protein_suggestion()

        if intent == "recipe_suggestion":
            return intent, self._build_recipe_suggestion(content)

        if intent == "meal_plan_summary":
            return intent, self._build_meal_plan_summary(current_user)

        if intent == "meal_swap":
            return intent, self._build_swap_suggestion(content)

        return (
            intent,
            (
                "I can currently help with these meal-assistant tasks:\n"
                "- summarize your calorie and macro goal\n"
                "- suggest high-protein foods\n"
                "- suggest recipes from your recipe catalog\n"
                "- suggest simple food swaps\n"
                "- summarize your latest meal plan"
            ),
        )

    # -------------------------------------------------------------------------
    # Public chat flow
    # -------------------------------------------------------------------------

    def send_message(
        self,
        current_user: User,
        chat_session_id: str,
        payload: ChatMessageCreateRequest,
    ) -> tuple[ChatMessage, ChatMessage]:
        session = self.get_session(current_user, chat_session_id)

        user_content = payload.content.strip()
        user_message = ChatMessage(
            chat_session_id=session.id,
            role="user",
            content=user_content,
            detected_intent=None,
            metadata_json=None,
        )
        self.db.add(user_message)
        self.db.flush()

        intent, assistant_content = self._generate_assistant_response(
            current_user=current_user,
            content=user_content,
        )

        assistant_message = ChatMessage(
            chat_session_id=session.id,
            role="assistant",
            content=assistant_content,
            detected_intent=intent,
            metadata_json=None,
        )
        self.db.add(assistant_message)

        if session.title == "New chat":
            session.title = user_content[:80]

        session.summary = assistant_content[:500]

        self.db.add(session)
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)

        return user_message, assistant_message