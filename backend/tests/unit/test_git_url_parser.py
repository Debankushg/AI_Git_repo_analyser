import pytest

from app.core.exceptions import BadRequestError
from app.utils.git_url_parser import parse_git_link


@pytest.mark.parametrize(
    "raw,host,path",
    [
        ("https://github.com/acme/app", "github.com", "acme/app"),
        ("acme/app", "github.com", "acme/app"),
        ("github.com/acme/app.git", "github.com", "acme/app"),
        ("git@github.com:acme/app.git", "github.com", "acme/app"),
        ("https://gitlab.com/group/sub/project", "gitlab.com", "group/sub/project"),
        ("git@gitlab.com:group/sub/project.git", "gitlab.com", "group/sub/project"),
        ("https://bitbucket.org/team/repo", "bitbucket.org", "team/repo"),
        ("https://dev.azure.com/org/proj/_git/repo", "dev.azure.com", "org/proj/_git/repo"),
        ("https://git.mycorp.com/team/app.git", "git.mycorp.com", "team/app"),
        ("ssh://git@git.mycorp.com:2222/team/app.git", "git.mycorp.com", "team/app"),
        ("https://gitea.example.org/me/tool", "gitea.example.org", "me/tool"),
    ],
)
def test_repo_forms(raw, host, path):
    p = parse_git_link(raw)
    assert (p.host, p.path, p.kind) == (host, path, "repo")


def test_gitlab_nested_blob_and_mr():
    p = parse_git_link("https://gitlab.com/group/sub/project/-/blob/main/src/a.py")
    assert (p.path, p.kind, p.ref, p.file_path) == ("group/sub/project", "blob", "main", "src/a.py")
    assert parse_git_link("https://gitlab.com/g/p/-/merge_requests/9").number == 9


def test_github_links():
    assert parse_git_link("https://github.com/a/b/tree/dev/src").file_path == "src"
    assert parse_git_link("https://github.com/a/b/pull/4").kind == "pull"
    assert parse_git_link("https://github.com/a/b/commit/abc").sha == "abc"


def test_bitbucket_and_gitea_paths():
    p = parse_git_link("https://bitbucket.org/t/r/src/main/lib/x.js")
    assert (p.ref, p.file_path, p.kind) == ("main", "lib/x.js", "blob")
    p = parse_git_link("https://git.corp.io/t/r/src/branch/dev/docs")
    assert (p.path, p.ref, p.file_path, p.kind) == ("t/r", "dev", "docs", "tree")


def test_credentials_only_in_clone_url():
    p = parse_git_link("https://user:secret@git.corp.io/t/r.git")
    assert p.path == "t/r" and "secret" not in p.path and "secret" in p.clone_url


@pytest.mark.parametrize("raw", ["", "hello", "file:///etc/passwd", "ext::sh -c id", "-oProxyCommand=x", "/etc/passwd", "ftp://a.com/x/y", "https://github.com/onlyowner", "gitlab.com/x"])
def test_invalid(raw):
    with pytest.raises(BadRequestError):
        parse_git_link(raw)
