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
    profile = service.get_profile(current_user)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this user.",
        )

    return service.to_profile_response(profile)


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