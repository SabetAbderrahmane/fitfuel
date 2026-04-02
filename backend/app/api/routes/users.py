from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserAccountResponse,
    UserProfileResponse,
    UserProfileUpsertRequest,
)
from app.services.auth_service import get_current_user
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserAccountResponse,
    summary="Get current authenticated user account",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserAccountResponse:
    return UserAccountResponse.model_validate(current_user)


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)

    try:
        return service.get_full_profile_response(current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Create or replace current user profile",
)
async def upsert_my_profile(
    payload: UserProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    return service.upsert_profile(current_user, payload)