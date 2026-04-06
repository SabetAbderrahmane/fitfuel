from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.meal_template import MealTemplateCreateRequest, MealTemplateResponse
from app.services.auth_service import get_current_user
from app.services.meal_template_service import MealTemplateService

router = APIRouter()


@router.post(
    "",
    response_model=MealTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a meal template",
)
async def create_meal_template(
    payload: MealTemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealTemplateResponse:
    service = MealTemplateService(db)
    template = service.create_template(current_user=current_user, payload=payload)
    return MealTemplateResponse.model_validate(template)


@router.get(
    "",
    response_model=list[MealTemplateResponse],
    summary="List meal templates",
)
async def list_meal_templates(
    q: str | None = Query(default=None, max_length=255),
    meal_slot: str | None = Query(default=None, max_length=30),
    category: str | None = Query(default=None, max_length=100),
    diet_type: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MealTemplateResponse]:
    _ = current_user
    service = MealTemplateService(db)
    templates = service.list_templates(
        query=q,
        meal_slot=meal_slot,
        category=category,
        diet_type=diet_type,
        limit=limit,
        offset=offset,
    )
    return [MealTemplateResponse.model_validate(template) for template in templates]


@router.get(
    "/{template_id}",
    response_model=MealTemplateResponse,
    summary="Get one meal template",
)
async def get_meal_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MealTemplateResponse:
    _ = current_user
    service = MealTemplateService(db)
    template = service.get_template(template_id)
    return MealTemplateResponse.model_validate(template)