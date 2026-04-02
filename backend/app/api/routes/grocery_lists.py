from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.grocery import (
    GroceryListGenerateFromMealPlanRequest,
    GroceryListItemResponse,
    GroceryListItemUpdateRequest,
    GroceryListResponse,
)
from app.services.auth_service import get_current_user
from app.services.grocery_service import GroceryService

router = APIRouter()


@router.post(
    "/from-meal-plan",
    response_model=GroceryListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a grocery list from a meal plan",
)
async def generate_grocery_list_from_meal_plan(
    payload: GroceryListGenerateFromMealPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroceryListResponse:
    service = GroceryService(db)
    grocery_list = service.generate_from_meal_plan(
        current_user=current_user,
        payload=payload,
    )
    return GroceryListResponse.model_validate(grocery_list)


@router.get(
    "",
    response_model=list[GroceryListResponse],
    summary="List grocery lists",
)
async def list_grocery_lists(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GroceryListResponse]:
    service = GroceryService(db)
    grocery_lists = service.list_grocery_lists(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [GroceryListResponse.model_validate(item) for item in grocery_lists]


@router.get(
    "/{grocery_list_id}",
    response_model=GroceryListResponse,
    summary="Get one grocery list",
)
async def get_grocery_list(
    grocery_list_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroceryListResponse:
    service = GroceryService(db)
    grocery_list = service.get_grocery_list(
        current_user=current_user,
        grocery_list_id=grocery_list_id,
    )
    return GroceryListResponse.model_validate(grocery_list)


@router.patch(
    "/items/{grocery_list_item_id}",
    response_model=GroceryListItemResponse,
    summary="Update grocery list item checked state",
)
async def update_grocery_list_item(
    grocery_list_item_id: str,
    payload: GroceryListItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroceryListItemResponse:
    service = GroceryService(db)
    item = service.update_grocery_list_item(
        current_user=current_user,
        grocery_list_item_id=grocery_list_item_id,
        payload=payload,
    )
    return GroceryListItemResponse.model_validate(item)