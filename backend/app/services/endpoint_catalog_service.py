"""Builds the list of API endpoints by introspecting the FastAPI app, so the UI is never out of date."""
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.schemas.meta_schemas import EndpointCatalogResponse, EndpointInfo

METHOD_ORDER = {"GET": 0, "POST": 1, "PUT": 2, "PATCH": 3, "DELETE": 4}


class EndpointCatalogService:
    def build(self, app: FastAPI) -> EndpointCatalogResponse:
        endpoints: list[EndpointInfo] = []
        for route in app.routes:
            if not isinstance(route, APIRoute) or not route.path.startswith("/api"):
                continue
            for method in sorted(route.methods - {"HEAD", "OPTIONS"}, key=lambda m: METHOD_ORDER.get(m, 9)):
                endpoints.append(
                    EndpointInfo(
                        method=method,
                        path=route.path,
                        category=route.tags[0] if route.tags else "other",
                        summary=route.summary or route.name.replace("_", " ").title(),
                    )
                )
        return EndpointCatalogResponse(total=len(endpoints), endpoints=endpoints)
