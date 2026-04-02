from fastapi import APIRouter

from app.api.routes.activity import router as activity_router
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.food_logs import router as food_logs_router
from app.api.routes.goals import router as goals_router
from app.api.routes.grocery_lists import router as grocery_lists_router
from app.api.routes.health import router as health_router
from app.api.routes.meal_plans import router as meal_plans_router
from app.api.routes.meals import router as meals_router
from app.api.routes.photos import router as photos_router
from app.api.routes.progress import router as progress_router
from app.api.routes.recipes import router as recipes_router
from app.api.routes.users import router as users_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(activity_router, prefix="/activity", tags=["Activity"])
api_router.include_router(goals_router, prefix="/goals", tags=["Goals"])
api_router.include_router(meals_router, prefix="/meals", tags=["Meals"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["Recipes"])
api_router.include_router(food_logs_router, prefix="/food-logs", tags=["Food Logs"])
api_router.include_router(progress_router, prefix="/progress", tags=["Progress"])
api_router.include_router(meal_plans_router, prefix="/meal-plans", tags=["Meal Plans"])
api_router.include_router(grocery_lists_router, prefix="/grocery-lists", tags=["Grocery Lists"])
api_router.include_router(photos_router, prefix="/photos", tags=["Photos"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])