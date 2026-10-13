from fastapi import FastAPI

from app.schemas.meta_schemas import EndpointCatalogResponse
from app.services.endpoint_catalog_service import EndpointCatalogService


class MetaController:
    def __init__(self, service: EndpointCatalogService) -> None:
        self._service = service

    def list_endpoints(self, app: FastAPI) -> EndpointCatalogResponse:
        return self._service.build(app)
