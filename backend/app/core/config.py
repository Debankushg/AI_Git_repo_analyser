from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    log_level: str = "INFO"

    # LLM
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    # GitHub / MCP
    github_personal_access_token: str = ""
    github_username: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]

    # GitHub MCP server over stdio via npx (no Docker needed). Override to use the Docker build.
    github_mcp_command: str = "npx"
    github_mcp_args: list[str] = ["-y", "@modelcontextprotocol/server-github"]

    # Other git hosts. Tokens per host, e.g. GIT_HOST_TOKENS={"gitlab.com":"glpat-...","git.mycorp.com":"..."}
    git_host_tokens: dict[str, str] = {}
    git_cache_dir: str = ""  # default: <system temp>/repo-assistant-clones
    git_cache_ttl_seconds: int = 600
    git_clone_depth: int = 100
    git_clone_timeout_seconds: int = 90

    # Tools that change GitHub state: never executed without user approval.
    write_tools: set[str] = {"create_issue", "create_pull_request"}
    max_agent_rounds: int = 8


settings = Settings()
