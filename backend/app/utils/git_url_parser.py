"""Turns anything a user might paste (GitHub, GitLab, Bitbucket, Azure DevOps, Gitea, self-hosted, SSH, .git)
into a structured location. Pure functions, no I/O."""
import re
from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlsplit

from app.core.exceptions import BadRequestError

_SEGMENT = re.compile(r"^[A-Za-z0-9._~@+-]+$")
_GITHUB_OWNER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_HOST = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$|^localhost$|^\d{1,3}(?:\.\d{1,3}){3}$")
_SCP = re.compile(r"^(?:(?P<user>[\w.-]+)@)?(?P<host>[\w.-]+\.[\w.-]+):(?!//)(?P<path>.+)$")
_MARKERS = {"tree", "blob", "src", "-", "commit", "commits", "pull", "pulls", "pull-requests", "merge_requests", "issues"}


@dataclass
class ParsedGitLink:
    host: str
    path: str  # repository path: "owner/name" or "group/subgroup/name"
    clone_url: str  # may contain credentials the user pasted: keep in memory only, never log or return
    kind: str = "repo"  # repo | tree | blob | pull | issue | commit
    ref: str | None = None  # branch / tag: first path segment (names containing "/" can't be detected from a URL)
    file_path: str = ""
    number: int | None = None
    sha: str | None = None


def parse_git_link(raw: str) -> ParsedGitLink:
    text = (raw or "").strip().strip("<>\"'")
    if not text:
        raise BadRequestError("Paste a repository link first.")
    if re.match(r"^(file|ext|data|javascript):", text, re.I) or text.startswith(("-", "/", ".", "~")):
        raise BadRequestError("That kind of link isn't supported. Use an https:// or ssh link to a repository.")

    userinfo, port, query = "", "", {}
    scheme = "https"
    scp = None if "://" in text else _SCP.match(text)
    if scp:  # git@host:group/repo.git
        host, path_text = scp["host"].lower(), scp["path"]
        scheme, userinfo = "scp", (scp["user"] + "@") if scp["user"] else ""
        clone_url = text
    else:
        if "://" in text:
            parts = urlsplit(text)
            if parts.scheme.lower() not in {"http", "https", "ssh", "git"}:
                raise BadRequestError("Only http(s) and ssh links are supported.")
            if not parts.hostname:
                raise BadRequestError("Could not find a host in that link.")
            scheme, host, path_text, query = parts.scheme.lower(), parts.hostname.lower(), parts.path, parse_qs(parts.query)
            port = f":{parts.port}" if parts.port else ""
            if parts.username:
                userinfo = parts.username + (f":{parts.password}" if parts.password else "") + "@"
        else:
            first, _, rest = text.partition("/")
            if _HOST.match(first.lower()):
                host, path_text = first.lower(), rest
            elif re.fullmatch(r"[\w.-]+/[\w.-]+", text):  # owner/repo shorthand -> GitHub
                host, path_text = "github.com", text
            else:
                raise BadRequestError("That doesn't look like a repository link. Try https://github.com/owner/repo")
            path_text = path_text.split("#")[0].split("?")[0]
        clone_url = ""

    segs = [unquote(s) for s in path_text.split("/") if s]
    if not _HOST.match(host):
        raise BadRequestError("Could not read a valid host from that link.")

    repo_segs, rest = _split_repo_path(host, segs)
    if repo_segs:
        repo_segs[-1] = re.sub(r"\.git$", "", repo_segs[-1])
    if len(repo_segs) < 2 or any(s in {".", ".."} or not _SEGMENT.fullmatch(s) for s in repo_segs):
        raise BadRequestError("Could not read an owner and repository name from that link.")
    if host == "github.com" and not _GITHUB_OWNER.fullmatch(repo_segs[0]):
        raise BadRequestError("Could not read an owner and repository name from that link.")

    path = "/".join(repo_segs)
    result = ParsedGitLink(host=host, path=path, clone_url=clone_url or f"{scheme}://{userinfo}{host}{port}/{path}.git")
    _apply_marker(result, rest, query)
    return result


def _split_repo_path(host: str, segs: list[str]) -> tuple[list[str], list[str]]:
    """Separate 'group/.../repo' from the trailing '/tree/main/src'-style part."""
    if "_git" in segs and (host == "dev.azure.com" or host.endswith(".visualstudio.com")):  # org/project/_git/repo
        i = segs.index("_git")
        return segs[: i + 2], segs[i + 2 :]
    if host == "github.com" or host == "bitbucket.org":
        return segs[:2], segs[2:]
    for i in range(2, len(segs)):  # GitLab nested groups, Gitea, self-hosted...
        if segs[i] in _MARKERS:
            return segs[:i], segs[i:]
    return list(segs), []


def _apply_marker(r: ParsedGitLink, rest: list[str], query: dict) -> None:
    if rest and rest[0] == "-":  # GitLab: /-/blob/main/x
        rest = rest[1:]
    if query.get("path"):  # Azure DevOps ?path=/a/b&version=GBmain
        r.file_path = query["path"][0].strip("/")
        v = (query.get("version") or [""])[0]
        r.ref = v[2:] if v.startswith(("GB", "GT")) else None
        r.kind = "blob" if "." in r.file_path.rsplit("/", 1)[-1] else "tree"
        return
    if not rest:
        return
    head, tail = rest[0], rest[1:]
    if head in {"tree", "blob"} and tail:
        r.kind, r.ref, r.file_path = head, tail[0], "/".join(tail[1:])
    elif head == "src" and tail:  # Bitbucket /src/main/a/b  or Gitea /src/branch/main/a/b
        if tail[0] in {"branch", "tag", "commit"} and len(tail) > 1:
            tail = tail[1:]
        r.ref, r.file_path = tail[0], "/".join(tail[1:])
        r.kind = "blob" if "." in (r.file_path.rsplit("/", 1)[-1] if r.file_path else "") else "tree"
    elif head in {"pull", "pulls", "pull-requests", "merge_requests"} and tail and tail[0].isdigit():
        r.kind, r.number = "pull", int(tail[0])
    elif head == "issues" and tail and tail[0].isdigit():
        r.kind, r.number = "issue", int(tail[0])
    elif head in {"commit", "commits"} and tail:
        r.kind, r.sha = "commit", tail[0]
