from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.failed_login_attempt import FailedLoginAttempt
from app.models.refresh_token import RefreshToken
from app.models.user import User


class AdminService:
    """
    Read-only admin/ops service for basic backend oversight.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def get_overview(self) -> dict:
        last_7_days = self._now() - timedelta(days=7)

        total_users = self.db.scalar(select(func.count(User.id))) or 0
        active_users = self.db.scalar(
            select(func.count(User.id)).where(User.is_active.is_(True))
        ) or 0

        total_refresh_tokens = self.db.scalar(
            select(func.count(RefreshToken.id))
        ) or 0
        active_refresh_tokens = self.db.scalar(
            select(func.count(RefreshToken.id)).where(
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > self._now(),
            )
        ) or 0

        recent_failed_logins = self.db.scalar(
            select(func.count(FailedLoginAttempt.id)).where(
                FailedLoginAttempt.created_at >= last_7_days
            )
        ) or 0

        recent_audit_events = self.db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.created_at >= last_7_days
            )
        ) or 0

        return {
            "total_users": int(total_users),
            "active_users": int(active_users),
            "total_refresh_tokens": int(total_refresh_tokens),
            "active_refresh_tokens": int(active_refresh_tokens),
            "recent_failed_logins": int(recent_failed_logins),
            "recent_audit_events": int(recent_audit_events),
        }

    def list_audit_logs(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        statement: Select[tuple[AuditLog]] = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_failed_login_attempts(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FailedLoginAttempt]:
        statement: Select[tuple[FailedLoginAttempt]] = (
            select(FailedLoginAttempt)
            .order_by(FailedLoginAttempt.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())