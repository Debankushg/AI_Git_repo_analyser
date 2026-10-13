from app.models.chat_model import ConversationMessage
from app.schemas.action_schemas import PendingActionResponse
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


class ChatController:
    def __init__(self, service: ChatService) -> None:
        self._service = service

    async def chat(self, req: ChatRequest) -> ChatResponse:
        messages = [ConversationMessage(m.role, m.content) for m in req.messages]
        result = await self._service.run(req.repo, messages)
        return ChatResponse(
            reply=result.reply,
            tool_calls=result.tool_calls,
            pending_actions=[PendingActionResponse.model_validate(a) for a in result.pending_actions],
        )
