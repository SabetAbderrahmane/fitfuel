from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    metadata = metadata


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


from app.models.ai_feedback_history import AIFeedbackHistory  # noqa: E402,F401
from app.models.audit_log import AuditLog  # noqa: E402,F401
from app.models.chat_message import ChatMessage  # noqa: E402,F401
from app.models.chat_session import ChatSession  # noqa: E402,F401
from app.models.failed_login_attempt import FailedLoginAttempt  # noqa: E402,F401
from app.models.food_item import FoodItem  # noqa: E402,F401
from app.models.food_log import FoodLog  # noqa: E402,F401
from app.models.food_log_item import FoodLogItem  # noqa: E402,F401
from app.models.grocery_list import GroceryList  # noqa: E402,F401
from app.models.grocery_list_item import GroceryListItem  # noqa: E402,F401
from app.models.meal_plan import MealPlan  # noqa: E402,F401
from app.models.meal_plan_item import MealPlanItem  # noqa: E402,F401
from app.models.nutrition_fact import NutritionFact  # noqa: E402,F401
from app.models.photo_prediction import PhotoPrediction  # noqa: E402,F401
from app.models.photo_upload import PhotoUpload  # noqa: E402,F401
from app.models.progress_snapshot import ProgressSnapshot  # noqa: E402,F401
from app.models.recipe import Recipe  # noqa: E402,F401
from app.models.recipe_ingredient import RecipeIngredient  # noqa: E402,F401
from app.models.refresh_token import RefreshToken  # noqa: E402,F401
from app.models.user import User  # noqa: E402,F401
from app.models.user_goal import UserGoal  # noqa: E402,F401
from app.models.user_profile import UserProfile  # noqa: E402,F401
from app.models.weight_log import WeightLog  # noqa: E402,F401