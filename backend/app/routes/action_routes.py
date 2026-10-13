from fastapi import APIRouter, Depends

from app.controllers.action_controller import ActionController
from app.core.dependencies import get_action_controller
from app.schemas.action_schemas import PendingActionResponse

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("", response_model=list[PendingActionResponse])
async def list_pending(ctrl: ActionController = Depends(get_action_controller)):
    return ctrl.list_pending()


@router.post("/{action_id}/approve", response_model=PendingActionResponse)
async def approve(action_id: str, ctrl: ActionController = Depends(get_action_controller)):
    return await ctrl.approve(action_id)


@router.post("/{action_id}/reject", response_model=PendingActionResponse)
async def reject(action_id: str, ctrl: ActionController = Depends(get_action_controller)):
    return ctrl.reject(action_id)
