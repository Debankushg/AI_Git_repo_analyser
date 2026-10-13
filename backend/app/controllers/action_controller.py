from app.schemas.action_schemas import PendingActionResponse
from app.services.approval_service import ApprovalService


class ActionController:
    def __init__(self, service: ApprovalService) -> None:
        self._service = service

    def list_pending(self) -> list[PendingActionResponse]:
        return [PendingActionResponse.model_validate(a) for a in self._service.list_pending()]

    async def approve(self, action_id: str) -> PendingActionResponse:
        return PendingActionResponse.model_validate(await self._service.approve(action_id))

    def reject(self, action_id: str) -> PendingActionResponse:
        return PendingActionResponse.model_validate(self._service.reject(action_id))
