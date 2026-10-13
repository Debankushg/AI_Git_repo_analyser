from typing import Literal

from pydantic import BaseModel

from app.schemas.action_schemas import PendingActionResponse


class ChatMessageSchema(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    repo: str  # "owner/name"
    messages: list[ChatMessageSchema]


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[str]
    pending_actions: list[PendingActionResponse]
