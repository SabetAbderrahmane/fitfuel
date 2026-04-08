from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.failed_login_attempt import FailedLoginAttempt
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import UserRegisterRequest


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthService:
    """
    Authentication service with access tokens, refresh tokens, failed login logging,
    and audit trail support.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _write_audit_log(
        self,
        action: str,
        user_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> None:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details_json=json.dumps(details) if details else None,
        )
        self.db.add(audit_log)

    def _write_failed_login(
        self,
        identifier: str,
        failure_reason: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        failed_attempt = FailedLoginAttempt(
            email=identifier.lower(),
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
        )
        self.db.add(failed_attempt)

    def _issue_refresh_token(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        raw_refresh_token = secrets.token_urlsafe(48)
        hashed_refresh_token = self._hash_token(raw_refresh_token)

        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh_token,
            expires_at=self._now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            revoked_at=None,
            created_from_ip=ip_address,
            user_agent=user_agent,
        )
        self.db.add(refresh_token)

        return raw_refresh_token

    def register_user(self, payload: UserRegisterRequest) -> User:
        existing_user = self.db.scalar(
            select(User).where(
                or_(
                    func.lower(User.email) == payload.email.lower(),
                    func.lower(User.username) == payload.username.lower(),
                )
            )
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email or username already exists.",
            )

        user = User(
            email=payload.email.lower(),
            username=payload.username,
            hashed_password=get_password_hash(payload.password),
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        self.db.add(user)
        self._write_audit_log(
            action="auth.register",
            user_id=None,
            entity_type="user",
            entity_id=None,
            details={"email": user.email, "username": user.username},
        )
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(
        self,
        identifier: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        normalized_identifier = identifier.strip().lower()

        user = self.db.scalar(
            select(User).where(
                or_(
                    func.lower(User.email) == normalized_identifier,
                    func.lower(User.username) == normalized_identifier,
                )
            )
        )

        if not user:
            self._write_failed_login(
                identifier=normalized_identifier,
                failure_reason="user_not_found",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.hashed_password):
            self._write_failed_login(
                identifier=normalized_identifier,
                failure_reason="invalid_password",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            self._write_failed_login(
                identifier=normalized_identifier,
                failure_reason="inactive_account",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        user.last_login_at = self._now()
        self.db.add(user)

        return user

    def create_token_pair(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        access_token = create_access_token(subject=user.id)
        refresh_token = self._issue_refresh_token(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self._write_audit_log(
            action="auth.login",
            user_id=user.id,
            entity_type="user",
            entity_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.commit()

        return access_token, refresh_token

    def refresh_access_token(
        self,
        raw_refresh_token: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        hashed = self._hash_token(raw_refresh_token)

        refresh_token = self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hashed)
        )

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if refresh_token.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked.",
            )

        if refresh_token.expires_at <= self._now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
            )

        user = self.db.get(User, refresh_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not available for refresh.",
            )

        refresh_token.revoked_at = self._now()
        self.db.add(refresh_token)

        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = self._issue_refresh_token(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self._write_audit_log(
            action="auth.refresh",
            user_id=user.id,
            entity_type="user",
            entity_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.commit()

        return new_access_token, new_refresh_token

    def revoke_refresh_token(
        self,
        current_user: User,
        raw_refresh_token: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        hashed = self._hash_token(raw_refresh_token)

        refresh_token = self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == hashed,
                RefreshToken.user_id == current_user.id,
            )
        )

        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found.",
            )

        if refresh_token.revoked_at is None:
            refresh_token.revoked_at = self._now()
            self.db.add(refresh_token)

        self._write_audit_log(
            action="auth.logout",
            user_id=current_user.id,
            entity_type="refresh_token",
            entity_id=refresh_token.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.commit()

    def revoke_all_refresh_tokens(
        self,
        current_user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> int:
        tokens = list(
            self.db.scalars(
                select(RefreshToken).where(
                    RefreshToken.user_id == current_user.id,
                    RefreshToken.revoked_at.is_(None),
                )
            ).all()
        )

        revoked_count = 0
        now = self._now()

        for token in tokens:
            token.revoked_at = now
            self.db.add(token)
            revoked_count += 1

        self._write_audit_log(
            action="auth.logout_all",
            user_id=current_user.id,
            entity_type="user",
            entity_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"revoked_tokens": revoked_count},
        )
        self.db.commit()

        return revoked_count


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, user_id)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def get_request_context(request: Request) -> tuple[str | None, str | None]:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else None

    user_agent = request.headers.get("user-agent")
    return client_ip, user_agent