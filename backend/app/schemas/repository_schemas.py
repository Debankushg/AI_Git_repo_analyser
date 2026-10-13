from typing import Literal

from pydantic import BaseModel


class RepositoryResponse(BaseModel):
    full_name: str
    description: str | None = None
    private: bool = False


class ContentEntryResponse(BaseModel):
    name: str
    path: str
    type: Literal["file", "dir"]


class FileResponse(BaseModel):
    path: str
    content: str = ""
    size: int = 0
    is_binary: bool = False
    truncated: bool = False
    image_data_url: str | None = None  # set for small images so the UI can preview them
    web_url: str | None = None  # the same file in the host's web UI


class RepositoryDetailResponse(BaseModel):
    id: str  # identifier to use in every other call ("owner/name" or "host/group/name")
    provider: str = "github"  # github | gitlab | git
    supports_pull_requests: bool = True
    pull_request_label: str = "Pull requests"
    full_name: str
    description: str | None = None
    private: bool = False
    default_branch: str | None = None
    language: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    html_url: str | None = None
    owner_avatar_url: str | None = None


class LinkTarget(BaseModel):
    """Where the pasted link points inside the repository."""

    kind: str  # repo | tree | blob | pull | issue | commit
    ref: str | None = None
    path: str = ""
    number: int | None = None
    sha: str | None = None


class ResolveRequest(BaseModel):
    url: str


class ResolveResponse(BaseModel):
    repository: RepositoryDetailResponse
    target: LinkTarget
