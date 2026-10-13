from fastapi import APIRouter, Depends

from app.controllers.chat_controller import ChatController
from app.core.dependencies import get_chat_controller
from app.schemas.chat_schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, ctrl: ChatController = Depends(get_chat_controller)):
    return await ctrl.chat(req)
