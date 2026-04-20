from app.models.activity_log import ActivityLog
from app.models.activity_profile import ActivityProfile
from app.models.ai_feedback_history import AIFeedbackHistory
from app.models.allergy import Allergy
from app.models.audit_log import AuditLog
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.classifier_label import ClassifierLabel
from app.models.classifier_label_food_map import ClassifierLabelFoodMap
from app.models.data_source import DataSource
from app.models.dietary_preference import DietaryPreference
from app.models.failed_login_attempt import FailedLoginAttempt
from app.models.food_alias import FoodAlias
from app.models.food_item import FoodItem
from app.models.food_log import FoodLog
from app.models.food_log_item import FoodLogItem
from app.models.food_source_link import FoodSourceLink
from app.models.grocery_list import GroceryList
from app.models.grocery_list_item import GroceryListItem
from app.models.ingestion_release import IngestionRelease
from app.models.meal_plan import MealPlan
from app.models.meal_plan_item import MealPlanItem
from app.models.meal_template import MealTemplate
from app.models.nutrition_fact import NutritionFact
from app.models.photo_prediction import PhotoPrediction
from app.models.photo_prediction_candidate import PhotoPredictionCandidate
from app.models.photo_upload import PhotoUpload
from app.models.progress_snapshot import ProgressSnapshot
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.refresh_token import RefreshToken
from app.models.source_food_record import SourceFoodRecord
from app.models.source_nutrient_record import SourceNutrientRecord
from app.models.user import User
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.models.weight_log import WeightLog


__all__ = [
    "User",
    "UserProfile",
    "ActivityProfile",
    "ActivityLog",
    "Allergy",
    "DietaryPreference",
    "UserGoal",
    "FoodItem",
    "FoodAlias",
    "FoodSourceLink",
    "NutritionFact",
    "DataSource",
    "IngestionRelease",
    "SourceFoodRecord",
    "SourceNutrientRecord",
    "Recipe",
    "RecipeIngredient",
    "MealTemplate",
    "FoodLog",
    "FoodLogItem",
    "WeightLog",
    "ProgressSnapshot",
    "MealPlan",
    "MealPlanItem",
    "GroceryList",
    "GroceryListItem",
    "PhotoUpload",
    "PhotoPrediction",
    "PhotoPredictionCandidate",
    "ClassifierLabel",
    "ClassifierLabelFoodMap",
    "ChatSession",
    "ChatMessage",
    "AIFeedbackHistory",
    "RefreshToken",
    "AuditLog",
    "FailedLoginAttempt",
]