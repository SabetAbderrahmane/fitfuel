from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreateRequest,
    ChatSessionCreateRequest,
    ChatSessionDetailResponse,
    ChatSessionSummaryResponse,
    ChatTurnResponse,
)
from app.services.auth_service import get_current_user
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatSessionSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a chat session",
)
async def create_chat_session(
    payload: ChatSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionSummaryResponse:
    service = ChatService(db)
    session = service.create_session(current_user=current_user, payload=payload)
    return ChatSessionSummaryResponse.model_validate(session)


@router.get(
    "/sessions",
    response_model=list[ChatSessionSummaryResponse],
    summary="List chat sessions",
)
async def list_chat_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSessionSummaryResponse]:
    service = ChatService(db)
    sessions = service.list_sessions(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return [ChatSessionSummaryResponse.model_validate(session) for session in sessions]


@router.get(
    "/sessions/{chat_session_id}",
    response_model=ChatSessionDetailResponse,
    summary="Get one chat session with messages",
)
async def get_chat_session(
    chat_session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionDetailResponse:
    service = ChatService(db)

    try:
        session = service.get_session(
            current_user=current_user,
            chat_session_id=chat_session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ChatSessionDetailResponse.model_validate(session)


@router.post(
    "/sessions/{chat_session_id}/messages",
    response_model=ChatTurnResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a user message and get assistant reply",
)
async def send_chat_message(
    chat_session_id: str,
    payload: ChatMessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatTurnResponse:
    service = ChatService(db)

    try:
        user_message, assistant_message = service.send_message(
            current_user=current_user,
            chat_session_id=chat_session_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ChatTurnResponse(
        session_id=chat_session_id,
        user_message=user_message,
        assistant_message=assistant_message,
    )