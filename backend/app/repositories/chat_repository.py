from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ChatSession)

    def get_session_for_user(
        self,
        user_id: str,
        chat_session_id: str,
    ) -> ChatSession | None:
        return self.db.scalar(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == chat_session_id,
                ChatSession.user_id == user_id,
            )
        )

    def list_sessions_for_user(
        self,
        user_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ChatSession]:
        statement = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_messages_for_session(
        self,
        chat_session_id: str,
    ) -> list[ChatMessage]:
        return list(
            self.db.scalars(
                select(ChatMessage)
                .where(ChatMessage.chat_session_id == chat_session_id)
                .order_by(ChatMessage.created_at.asc())
            ).all()
        )