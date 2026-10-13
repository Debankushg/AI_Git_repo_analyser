from typing import Literal

from pydantic import BaseModel, ConfigDict


class PendingActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tool: str
    arguments: dict
    summary: str
    status: Literal["pending", "approved", "rejected"]
    result: str | None = None
