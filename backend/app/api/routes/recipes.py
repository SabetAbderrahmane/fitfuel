from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.recipe import RecipeCreateRequest, RecipeResponse
from app.services.auth_service import get_current_user
from app.services.recipe_service import RecipeService

router = APIRouter()


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recipe",
)
async def create_recipe(
    payload: RecipeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecipeResponse:
    service = RecipeService(db)
    recipe = service.create_recipe(current_user=current_user, payload=payload)
    return RecipeResponse.model_validate(recipe)


@router.get(
    "",
    response_model=list[RecipeResponse],
    summary="List recipes",
)
async def list_recipes(
    q: str | None = Query(default=None, max_length=255),
    category: str | None = Query(default=None, max_length=100),
    diet_type: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RecipeResponse]:
    _ = current_user
    service = RecipeService(db)
    recipes = service.list_recipes(
        query=q,
        category=category,
        diet_type=diet_type,
        limit=limit,
        offset=offset,
    )
    return [RecipeResponse.model_validate(recipe) for recipe in recipes]


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get one recipe",
)
async def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecipeResponse:
    _ = current_user
    service = RecipeService(db)
    recipe = service.get_recipe(recipe_id)
    return RecipeResponse.model_validate(recipe)