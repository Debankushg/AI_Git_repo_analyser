"""Browser links for files/commits on the common git hosts."""
from urllib.parse import quote

from app.models.repo_ref_model import RepoRef


def host_family(host: str) -> str:
    h = host.lower()
    if h == "github.com":
        return "github"
    if "gitlab" in h:
        return "gitlab"
    if h == "bitbucket.org":
        return "bitbucket"
    if h == "dev.azure.com" or h.endswith(".visualstudio.com"):
        return "azure"
    return "other"


def web_base(ref: RepoRef) -> str:
    return f"https://{ref.host}/{ref.path}"


def file_url(ref: RepoRef, branch: str, path: str) -> str | None:
    base, fam, p = web_base(ref), host_family(ref.host), quote(path)
    if fam == "github":
        return f"{base}/blob/{quote(branch)}/{p}"
    if fam == "gitlab":
        return f"{base}/-/blob/{quote(branch)}/{p}"
    if fam == "bitbucket":
        return f"{base}/src/{quote(branch)}/{p}"
    if fam == "azure":
        return f"{base}?path=/{p}&version=GB{quote(branch)}"
    return base


def commit_url(ref: RepoRef, sha: str) -> str | None:
    base, fam = web_base(ref), host_family(ref.host)
    if fam in {"github", "azure"}:
        return f"{base}/commit/{sha}"
    if fam == "gitlab":
        return f"{base}/-/commit/{sha}"
    if fam == "bitbucket":
        return f"{base}/commits/{sha}"
    return None
