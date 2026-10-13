from pydantic import BaseModel


class EndpointInfo(BaseModel):
    method: str
    path: str
    category: str
    summary: str


class EndpointCatalogResponse(BaseModel):
    total: int
    endpoints: list[EndpointInfo]
