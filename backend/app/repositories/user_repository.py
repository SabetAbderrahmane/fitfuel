from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(
            select(User).where(User.email == email.lower())
        )

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(
            select(User).where(User.username == username)
        )

    def get_by_email_or_username(
        self,
        *,
        email: str,
        username: str,
    ) -> User | None:
        return self.db.scalar(
            select(User).where(
                or_(
                    User.email == email.lower(),
                    User.username == username,
                )
            )
        )

    def get_with_profile(self, user_id: str) -> User | None:
        return self.db.scalar(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )

    def list_recent_users(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        statement = (
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())