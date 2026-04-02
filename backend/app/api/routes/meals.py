from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.meal import FoodItemCreateRequest, FoodItemResponse
from app.services.auth_service import get_current_user
from app.services.meal_service import MealService

router = APIRouter()


@router.post(
    "/foods",
    response_model=FoodItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a food catalog item",
)
async def create_food_item(
    payload: FoodItemCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodItemResponse:
    _ = current_user
    service = MealService(db)
    food_item = service.create_food_item(payload)
    return FoodItemResponse.model_validate(food_item)


@router.get(
    "/foods",
    response_model=list[FoodItemResponse],
    summary="List food catalog items",
)
async def list_food_items(
    q: str | None = Query(default=None, max_length=255),
    category: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FoodItemResponse]:
    _ = current_user
    service = MealService(db)
    items = service.list_food_items(
        query=q,
        category=category,
        limit=limit,
        offset=offset,
    )
    return [FoodItemResponse.model_validate(item) for item in items]


@router.get(
    "/foods/{food_item_id}",
    response_model=FoodItemResponse,
    summary="Get one food catalog item",
)
async def get_food_item(
    food_item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FoodItemResponse:
    _ = current_user
    service = MealService(db)
    item = service.get_food_item(food_item_id)
    return FoodItemResponse.model_validate(item)