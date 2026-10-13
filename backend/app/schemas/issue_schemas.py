from pydantic import BaseModel, ConfigDict


class IssueResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    state: str = "open"
    html_url: str | None = None
    labels: list[dict | str] = []


class PullRequestResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    draft: bool = False
    html_url: str | None = None
    user: dict | None = None
    created_at: str | None = None
