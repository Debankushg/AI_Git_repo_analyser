from dataclasses import dataclass

from app.core.exceptions import BadRequestError

GITHUB_HOST = "github.com"


@dataclass(frozen=True)
class RepoRef:
    """Identifies a repository on any git host.

    id format: GitHub repos stay "owner/name"; every other host is "host/group/.../name"
    (GitHub owners can't contain dots, so a dotted first segment always means a host)."""

    host: str
    path: str  # "owner/name" or "group/subgroup/name"

    @property
    def id(self) -> str:
        return self.path if self.host == GITHUB_HOST else f"{self.host}/{self.path}"

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def owner(self) -> str:
        return self.path.rsplit("/", 1)[0] if "/" in self.path else ""

    @staticmethod
    def from_id(repo_id: str) -> "RepoRef":
        parts = [p for p in (repo_id or "").strip().strip("/").split("/") if p]
        if parts and "." in parts[0]:
            host, path_parts = parts[0].lower(), parts[1:]
        else:
            host, path_parts = GITHUB_HOST, parts
        if len(path_parts) < 2 or any(p in {".", ".."} for p in path_parts):
            raise BadRequestError("Invalid repository identifier.")
        return RepoRef(host=host, path="/".join(path_parts))
