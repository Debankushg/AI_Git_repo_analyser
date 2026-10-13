# Backend architecture

Layered design. A request only ever travels **down** one layer at a time.

```
HTTP request
  │
  ▼ middlewares/        request logging, CORS, error → JSON
  ▼ routes/             URL + HTTP verb, Depends() wiring, response_model
  ▼ controllers/        translate HTTP schemas <-> domain models (no business logic)
  ▼ services/           business logic and the agent loop
  │    ├─► llm/               LLM provider (Gemini) behind a neutral interface
  │    └─► repositories/      data access
  │            └─► mcp_layer/client  ──stdio──►  mcp_layer/server (GitHub MCP server process) ──► GitHub
```

## Folders

| Folder | Responsibility | Example |
|---|---|---|
| `main.py` | App factory, lifespan (starts/stops MCP), middleware registration | |
| `core/` | config, logging, exceptions, **dependencies.py** (wiring of every object) | `config.py` |
| `middlewares/` | Cross-cutting HTTP concerns | `error_handler_middleware.py` |
| `routes/` | Endpoint declarations only | `chat_routes.py` |
| `controllers/` | Adapter between routes and services | `chat_controller.py` |
| `services/` | Business rules: `chat_service` (agent loop), `approval_service`, `repository_service`, `issue_service` | |
| `repositories/` | Data access: `github_repository` (via MCP), `action_repository` (pending actions store) | |
| `llm/` | `base_llm_provider.py` interface, `gemini_provider.py`, `llm_factory.py`, `prompts/` | |
| `mcp_layer/client/` | MCP **client**: protocol calls to the server | `github_mcp_client.py` |
| `mcp_layer/server/` | MCP **server** launch config (server is an external program) | `github_server_config.py` |
| `mcp_layer/tool_policy.py` | Which tools need approval; forced safe args (draft PRs) | |
| `models/` | Internal domain objects (dataclasses) | `pending_action_model.py` |
| `schemas/` | API request/response DTOs (Pydantic) | `chat_schemas.py` |
| `tests/` | Unit tests | |

Models vs schemas: **models** are internal entities passed between services; **schemas** are the JSON shapes the frontend sees.

## Workflow: "Find the highest-priority bug"

1. `POST /api/chat` → `chat_routes.py` → `ChatController.chat()` converts schema → `ConversationMessage`s.
2. `ChatService.run()` asks `GitHubRepository.list_tools()` (→ MCP client → server) for the tool list.
3. It opens an LLM session (`llm_factory` → `GeminiProvider.new_session`) with the system prompt + tools.
4. Loop (max `max_agent_rounds`): `session.generate()` → Gemini returns text or tool calls.
5. Read tool (e.g. `list_issues`) → `GitHubRepository.call_tool` → MCP client → GitHub; output returns to the LLM.
6. Write tool (`create_issue`, `create_pull_request`) → `tool_policy.is_write_tool` → `ApprovalService.queue()`; **not executed**.
7. Final text + queued actions return up through the controller as `ChatResponse`.
8. User clicks Approve → `POST /api/actions/{id}/approve` → `ApprovalService.approve()` runs the tool.

Errors: services raise `AppError` subclasses (`core/exceptions.py`); the error-handler middleware maps them to HTTP status codes (e.g. Gemini 429 → `RateLimitError` → 429).

## Extending

- New LLM: add `llm/<name>_provider.py` implementing `BaseLLMProvider`, register it in `llm_factory.py`.
- New endpoint: schema → service method → controller method → route → wire in `core/dependencies.py`.
- Persist actions in a DB: reimplement `ActionRepository` with the same methods.
