"""Safety rules for MCP tools. Single place that decides which tools need human approval."""
from app.core.config import settings


def is_write_tool(tool_name: str) -> bool:
    return tool_name in settings.write_tools


def apply_safety_defaults(tool_name: str, args: dict) -> dict:
    """Force safe options on risky tools (pull requests are always drafts)."""
    safe = dict(args)
    if tool_name == "create_pull_request":
        safe["draft"] = True
    return safe
