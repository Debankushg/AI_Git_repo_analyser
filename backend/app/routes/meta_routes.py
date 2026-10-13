from fastapi import APIRouter, Depends, Request

from app.controllers.meta_controller import MetaController
from app.core.dependencies import get_meta_controller
from app.schemas.meta_schemas import EndpointCatalogResponse

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/endpoints", response_model=EndpointCatalogResponse)
async def list_endpoints(request: Request, ctrl: MetaController = Depends(get_meta_controller)):
    return ctrl.list_endpoints(request.app)
