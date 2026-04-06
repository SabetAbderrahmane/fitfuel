from fastapi import APIRouter, Depends, Request, status

from app.models.user import User
from app.schemas.auth import (
    AuthenticatedUserResponse,
    LogoutRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import (
    AuthService,
    get_auth_service,
    get_current_user,
    get_request_context,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthenticatedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUserResponse:
    user = auth_service.register_user(payload)
    return AuthenticatedUserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return access + refresh tokens",
)
async def login(
    payload: UserLoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip_address, user_agent = get_request_context(request)
    user = auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    access_token, refresh_token = auth_service.create_token_pair(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a refresh token",
)
async def refresh_token(
    payload: TokenRefreshRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip_address, user_agent = get_request_context(request)
    access_token, refresh_token = auth_service.refresh_access_token(
        raw_refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke one refresh token",
)
async def logout(
    payload: LogoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    ip_address, user_agent = get_request_context(request)
    auth_service.revoke_refresh_token(
        current_user=current_user,
        raw_refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return MessageResponse(message="Refresh token revoked successfully.")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke all refresh tokens for current user",
)
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    ip_address, user_agent = get_request_context(request)
    revoked_count = auth_service.revoke_all_refresh_tokens(
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return MessageResponse(
        message=f"Revoked {revoked_count} refresh token(s)."
    )


@router.get(
    "/me",
    response_model=AuthenticatedUserResponse,
    summary="Get current authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse.model_validate(current_user)