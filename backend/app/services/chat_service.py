from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload
from rapidfuzz import fuzz

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.food_item import FoodItem
from app.models.recipe import Recipe
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest


class ChatService:
    """
    Deterministic meal assistant service.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.goal_repository = GoalRepository(db)
        self.meal_plan_repository = MealPlanRepository(db)

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

    def _list_top_protein_foods(self, limit: int = 5) -> list[FoodItem]:
        items = list(
            self.db.scalars(
                select(FoodItem)
                .options(selectinload(FoodItem.nutrition_fact))
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.name.asc())
            ).all()
        )
        items = [item for item in items if item.nutrition_fact is not None]
        items.sort(
            key=lambda item: item.nutrition_fact.protein_g_per_100g if item.nutrition_fact else 0,
            reverse=True,
        )
        return items[:limit]

    def _build_high_protein_suggestion(self) -> str:
        foods = self._list_top_protein_foods(limit=5)

        if not foods:
            return "I could not find any food catalog items with nutrition facts yet."

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

    def _find_best_matching_food(self, query_text: str) -> FoodItem | None:
        items = list(
            self.db.scalars(
                select(FoodItem)
                .options(selectinload(FoodItem.nutrition_fact))
                .where(FoodItem.is_active.is_(True))
            ).all()
        )

        best_item: FoodItem | None = None
        best_score = 0.0
        lowered = query_text.lower()

        for item in items:
            score = float(fuzz.token_sort_ratio(lowered, item.name.lower()))
            if score > best_score:
                best_score = score
                best_item = item

        if best_item is None or best_score < 55:
            return None

        return best_item

    def _build_swap_suggestion(self, content: str) -> str:
        referenced_food = self._find_best_matching_food(content)

        if referenced_food is None:
            return (
                "I could not confidently detect which food you want to swap. "
                "Mention the food name more clearly, for example: "
                "`swap chicken breast for another protein`."
            )

        candidates = list(
            self.db.scalars(
                select(FoodItem)
                .options(selectinload(FoodItem.nutrition_fact))
                .where(FoodItem.is_active.is_(True))
                .order_by(FoodItem.name.asc())
            ).all()
        )

        same_category = [
            item
            for item in candidates
            if item.id != referenced_food.id
            and item.nutrition_fact is not None
            and referenced_food.category
            and item.category == referenced_food.category
        ]

        if not same_category:
            same_category = [
                item
                for item in candidates
                if item.id != referenced_food.id and item.nutrition_fact is not None
            ]

        same_category.sort(
            key=lambda item: item.nutrition_fact.protein_g_per_100g if item.nutrition_fact else 0,
            reverse=True,
        )

        suggestions = same_category[:3]

        if not suggestions:
            return f"I found **{referenced_food.name}**, but I could not find good swap candidates yet."

        lines = [f"Possible swaps for **{referenced_food.name}**:"]
        for item in suggestions:
            nutrition = item.nutrition_fact
            assert nutrition is not None
            lines.append(
                f"- **{item.name}**: {nutrition.calories_per_100g} kcal / 100 g, "
                f"{nutrition.protein_g_per_100g} g protein / 100 g"
            )

        return "\n".join(lines)

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