from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import UserGoalCreateRequest, UserGoalResponse
from app.services.auth_service import get_current_user
from app.services.goal_service import GoalService

router = APIRouter()


@router.post(
    "",
    response_model=UserGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new active goal",
)
async def create_goal(
    payload: UserGoalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserGoalResponse:
    service = GoalService(db)
    goal = service.create_goal(current_user, payload)
    return UserGoalResponse.model_validate(goal)


@router.get(
    "",
    response_model=list[UserGoalResponse],
    summary="List all goals for current user",
)
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UserGoalResponse]:
    service = GoalService(db)
    goals = service.list_goals(current_user)
    return [UserGoalResponse.model_validate(goal) for goal in goals]


@router.get(
    "/current",
    response_model=UserGoalResponse,
    summary="Get current active goal",
)
async def get_current_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserGoalResponse:
    service = GoalService(db)
    goal = service.get_current_goal(current_user)
    return UserGoalResponse.model_validate(goal)