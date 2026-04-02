from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.food_log import FoodLogCreateRequest, FoodLogResponse, MealType
from app.services.auth_service import get_current_user
from app.services.food_log_service import FoodLogService

router = APIRouter()


@router.post(
    "",
    response_model=FoodLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a manual food log",
)
async def create_food_log(
    payload: FoodLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodLogResponse:
    service = FoodLogService(db)
    food_log = service.create_food_log(current_user=current_user, payload=payload)
    return FoodLogResponse.model_validate(food_log)


@router.get(
    "",
    response_model=list[FoodLogResponse],
    summary="List current user's food logs",
)
async def list_food_logs(
    logged_for_date: date | None = Query(default=None),
    meal_type: MealType | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FoodLogResponse]:
    service = FoodLogService(db)
    logs = service.list_food_logs(
        current_user=current_user,
        logged_for_date=logged_for_date,
        meal_type=meal_type,
        limit=limit,
        offset=offset,
    )
    return [FoodLogResponse.model_validate(log) for log in logs]


@router.get(
    "/{food_log_id}",
    response_model=FoodLogResponse,
    summary="Get one food log",
)
async def get_food_log(
    food_log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodLogResponse:
    service = FoodLogService(db)
    log = service.get_food_log(
        current_user=current_user,
        food_log_id=food_log_id,
    )
    return FoodLogResponse.model_validate(log)