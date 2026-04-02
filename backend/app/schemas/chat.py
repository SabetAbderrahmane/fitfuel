from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class ChatMessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_session_id: str
    role: str
    content: str
    detected_intent: str | None
    metadata_json: str | None
    created_at: datetime
    updated_at: datetime


class ChatSessionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    status: str
    summary: str | None
    created_at: datetime
    updated_at: datetime


class ChatSessionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    status: str
    summary: str | None
    messages: list[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime


class ChatTurnResponse(BaseModel):
    session_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse