from app.mcp_layer import tool_policy


def test_write_tools_need_approval():
    assert tool_policy.is_write_tool("create_issue")
    assert not tool_policy.is_write_tool("list_issues")


def test_pull_requests_forced_to_draft():
    assert tool_policy.apply_safety_defaults("create_pull_request", {"title": "x"})["draft"] is True
