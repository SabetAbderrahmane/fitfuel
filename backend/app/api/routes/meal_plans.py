from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.meal_plan import (
    MealPlanCreateRequest,
    MealPlanGenerateRequest,
    MealPlanResponse,
)
from app.services.auth_service import get_current_user
from app.services.meal_plan_service import MealPlanService

router = APIRouter()


@router.post(
    "",
    response_model=MealPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a manual meal plan",
)
async def create_meal_plan(
    payload: MealPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealPlanResponse:
    service = MealPlanService(db)
    plan = service.create_meal_plan(current_user=current_user, payload=payload)
    return MealPlanResponse.model_validate(plan)


@router.post(
    "/generate",
    response_model=MealPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a simple rule-based meal plan",
)
async def generate_meal_plan(
    payload: MealPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealPlanResponse:
    service = MealPlanService(db)
    plan = service.generate_meal_plan(current_user=current_user, payload=payload)
    return MealPlanResponse.model_validate(plan)


@router.get(
    "",
    response_model=list[MealPlanResponse],
    summary="List current user's meal plans",
)
async def list_meal_plans(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MealPlanResponse]:
    service = MealPlanService(db)
    plans = service.list_meal_plans(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [MealPlanResponse.model_validate(plan) for plan in plans]


@router.get(
    "/{meal_plan_id}",
    response_model=MealPlanResponse,
    summary="Get one meal plan",
)
async def get_meal_plan(
    meal_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealPlanResponse:
    service = MealPlanService(db)
    plan = service.get_meal_plan(
        current_user=current_user,
        meal_plan_id=meal_plan_id,
    )
    return MealPlanResponse.model_validate(plan)
