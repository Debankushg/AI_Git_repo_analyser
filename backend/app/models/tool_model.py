from dataclasses import dataclass, field


@dataclass
class ToolSpec:
    """A tool advertised by the MCP server and offered to the LLM."""

    name: str
    description: str
    input_schema: dict


@dataclass
class ToolCall:
    """The LLM asking us to run a tool."""

    name: str
    args: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    name: str
    output: str
