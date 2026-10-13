from pydantic import BaseModel


class CommitResponse(BaseModel):
    sha: str
    message: str  # full commit message; the UI shows the first line as the title
    author_name: str
    author_login: str | None = None
    avatar_url: str | None = None
    date: str | None = None  # ISO 8601
    html_url: str | None = None
