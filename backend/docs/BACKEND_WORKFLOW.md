# Backend Workflow Guide (main.py → end)

This guide shows **which folder connects to which**, starting at `main.py`, and walks through
each request step by step. Read top to bottom; each section builds on the previous one.

---

## 1. The big picture

```
┌────────────┐   HTTP    ┌────────────────────────── FastAPI backend ──────────────────────────┐
│  React UI  │ ────────► │  main.py → middlewares → routes → controllers → services            │
│ (frontend) │ ◄──────── │                                        │                            │
└────────────┘   JSON    │                          ┌─────────────┴──────────────┐             │
                         │                          ▼                            ▼             │
                         │                    llm/ (Gemini)              repositories/         │
                         │                          │                            │             │
                         └──────────────────────────┼────────────────────────────┼─────────────┘
                                                    ▼                            ▼
                                             Google Gemini API        mcp_layer/client (MCP client)
                                                                                 │ stdio
                                                                                 ▼
                                                                  GitHub MCP server (npx process)
                                                                                 │ HTTPS
                                                                                 ▼
                                                                             GitHub API
```

Three external systems: **Gemini** (the brain), **MCP server** (the tool box), **GitHub** (the data).
Everything else in `backend/app/` is our own code that connects them safely.

---

## 2. Startup: what `main.py` connects

```
                                   main.py
                                      │
        ┌──────────────┬──────────────┼───────────────────┬───────────────────┐
        ▼              ▼              ▼                   ▼                   ▼
  core/config.py  core/logging_   middlewares/      routes/api_router.py   core/dependencies.py
  (settings from  config.py       • request_logging   (all endpoints)      → get_mcp_client()
   .env)          (log format)    • error_handler                              │
                                  (+ CORS)                                      ▼
                                                                  lifespan: mcp_client.start()
                                                                  launches the GitHub MCP server
                                                                  subprocess (mcp_layer/server/)
```

| Step | What happens | File |
|---|---|---|
| 1 | `create_app()` builds the FastAPI app | [main.py](../app/main.py) |
| 2 | Adds `RequestLoggingMiddleware` and CORS | [request_logging_middleware.py](../app/middlewares/request_logging_middleware.py) |
| 3 | Registers error handlers (domain errors → JSON) | [error_handler_middleware.py](../app/middlewares/error_handler_middleware.py) |
| 4 | Includes `api_router` (all `/api/...` endpoints) | [api_router.py](../app/routes/api_router.py) |
| 5 | On startup (`lifespan`): sets up logging, then `mcp.start()` | [main.py](../app/main.py) |
| 6 | `start()` reads launch command from config and spawns the MCP server over stdio | [github_server_config.py](../app/mcp_layer/server/github_server_config.py), [github_mcp_client.py](../app/mcp_layer/client/github_mcp_client.py) |
| 7 | On shutdown: `mcp.stop()` closes the subprocess | [main.py](../app/main.py) |

If startup fails with `FileNotFoundError`, the MCP launch command (`npx` / `docker`) is not installed.

---

## 3. Layer map: who calls whom

Each arrow means "imports and calls". A layer never skips downward and **never calls upward**.

```
 routes/  ─────►  controllers/  ─────►  services/  ─────►  repositories/  ─────►  mcp_layer/client
 (URL)            (adapter)             (logic)             (data access)           (MCP protocol)
    │                 │                    │  │                                         │
    │                 │                    │  └────────►  llm/  ───► Gemini API         ▼
    │                 │                    │                                      MCP server → GitHub
    ▼                 ▼                    ▼
 schemas/          schemas/ + models/    models/
 (JSON shapes)     (convert between)     (internal objects)

 core/dependencies.py creates every object above and injects it (the "wiring").
 core/exceptions.py defines errors that services raise; middlewares turn them into HTTP responses.
```

| Folder | One-line job | Talks to |
|---|---|---|
| `routes/` | Declare URL + method, pick the controller | controllers |
| `controllers/` | Convert API schema ⇄ internal model, call a service | services |
| `services/` | Business rules and the agent loop | llm, repositories |
| `providers/` | One class per git host behind `BaseGitProvider`: GitHub (MCP), GitLab (REST), any other host (`git` CLI clone) | repositories, mcp_layer |
| `repositories/` | Fetch/store data | mcp_layer/client, memory store |
| `llm/` | Talk to the AI model | Gemini API |
| `mcp_layer/client/` | Speak MCP protocol | MCP server |
| `mcp_layer/server/` | How to launch the MCP server | (config only) |
| `mcp_layer/tool_policy.py` | Which tools need approval | used by chat_service |
| `utils/` | Pure helpers, e.g. `github_url_parser.py` (any GitHub link → owner/repo/branch/path) | services |
| `models/` | Internal data objects | used by all layers |
| `schemas/` | JSON request/response shapes | routes, controllers |
| `middlewares/` | Logging, error → JSON | wraps every request |
| `core/` | Config, logging, errors, wiring | everything |

---

## 4. Workflow A: Simple data request (no AI)

Example: user selects a repository, the UI loads its issues → `GET /api/repositories/acme/app/issues`

```
 ① Browser          GET /api/repositories/acme/app/issues
        │
        ▼
 ② middlewares/request_logging_middleware.py     starts timer, assigns request id
        │
        ▼
 ③ routes/issue_routes.py  list_issues()         matches URL; Depends(get_issue_controller)
        │
        ▼
 ④ controllers/issue_controller.py               calls the service
        │
        ▼
 ⑤ services/issue_service.py                     asks repo for data, keeps only open issues,
        │                                        maps each to IssueResponse (schemas/issue_schemas.py)
        ▼
 ⑥ repositories/github_repository.py             list_issues(owner, repo)
        │
        ▼
 ⑦ mcp_layer/client/github_mcp_client.py         call_tool("list_issues", {...}) over stdio
        │
        ▼
 ⑧ GitHub MCP server  ───►  GitHub API           returns JSON
        │
        ▼ (response travels back up: ⑦ → ⑥ → ⑤ → ④ → ③ → ②)
 ⑨ middleware adds X-Request-ID header, logs "GET /api/... 200 120ms"
        │
        ▼
 ⑩ Browser receives JSON list of issues
```

The Explorer (`/contents`, `/file`) and Pull Requests (`/pulls`) endpoints follow the same shape using
`repository_*` and `issue_*` files. The repository dropdown is `GET /api/repositories`.

---

## 5. Workflow B: AI chat request (the agent loop)

Example: *"Find the highest-priority bug and tell me which files to change"* → `POST /api/chat`

```
 ① Browser  POST /api/chat  {repo: "acme/app", messages: [...]}
      │
      ▼
 ② middlewares → ③ routes/chat_routes.py → ④ controllers/chat_controller.py
      │          converts ChatRequest (schema) into ConversationMessage list (models/chat_model.py)
      ▼
 ⑤ services/chat_service.py  run()
      │
      ├─⑥ repositories/github_repository.list_tools() ─► MCP client ─► MCP server
      │       returns the tool list (list_issues, get_file_contents, search_code, create_issue, ...)
      │
      ├─⑦ llm/llm_factory → llm/gemini_provider.new_session(system prompt, messages, tools)
      │       system prompt comes from llm/prompts/repo_assistant_prompt.py
      │
      └─⑧ LOOP (up to settings.max_agent_rounds, default 8)
            │
            │   ┌──────────────────────────────────────────────────────────────┐
            │   │ 8a. session.generate()  ──► Gemini API                       │
            │   │      returns: text   OR   tool call(s)                       │
            │   │                                                              │
            │   │ 8b. no tool calls?  ──► STOP, text is the final answer       │
            │   │                                                              │
            │   │ 8c. for each tool call:                                      │
            │   │      is it a WRITE tool?  (mcp_layer/tool_policy.py)         │
            │   │        │                                                     │
            │   │   NO ──┤► github_repository.call_tool ─► MCP ─► GitHub       │
            │   │        │   output (trimmed to 20k chars) is the tool result  │
            │   │        │                                                     │
            │   │  YES ──┘► approval_service.queue()  (NOT executed)           │
            │   │            tool result = "Queued for approval"               │
            │   │            PRs are forced to draft=True                      │
            │   │                                                              │
            │   │ 8d. session.add_tool_results(...) ──► back to 8a             │
            │   └──────────────────────────────────────────────────────────────┘
            │
            ▼
 ⑨ AgentResult(reply, tool_calls, pending_actions)  returned to the controller
      │
      ▼
 ⑩ controller maps models → ChatResponse (schemas/chat_schemas.py) → JSON to browser
      │
      ▼
 ⑪ UI shows the reply in Chat + AI Analysis, and any pending actions in Action Approval
```

Typical tool sequence for the example question:
`list_issues` → `get_issue` → `search_code` → `get_file_contents` → final answer.
Each round is **one Gemini request**, so one question can use several requests (matters for free-tier limits).

---

## 6. Workflow C: Approving an action

The AI never writes to GitHub directly. Writes are queued, then a human approves.

```
 AI wants create_issue / create_pull_request
        │
        ▼
 chat_service → approval_service.queue()
        │          creates PendingActionModel (models/pending_action_model.py)
        ▼          saves it via repositories/action_repository.py (in memory)
 UI shows an approval card with the exact title/body

 ┌── user clicks Approve ───────────────────────────────────────────────────────┐
 │ POST /api/actions/{id}/approve                                               │
 │   routes/action_routes.py → controllers/action_controller.py                 │
 │   → services/approval_service.approve()                                      │
 │        → repositories/github_repository.call_tool(tool, args)                │
 │        → MCP client → MCP server → GitHub creates the issue / DRAFT PR       │
 │        status = "approved", result saved, returned to UI                     │
 └──────────────────────────────────────────────────────────────────────────────┘
 ┌── user clicks Reject ────────────────────────────────────────────────────────┐
 │ POST /api/actions/{id}/reject → approval_service.reject() → status "rejected"│
 │ Nothing is sent to GitHub.                                                   │
 └──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Workflow D: Errors

```
 Gemini returns 429 (quota)         GitHub/MCP tool fails          Anything unexpected
          │                                  │                              │
 llm/gemini_provider.py             mcp_layer/client raises          (any layer)
 raises RateLimitError              UpstreamError                    plain Exception
          │                                  │                              │
          └──────────────┬───────────────────┘                              │
                         ▼                                                  ▼
        middlewares/error_handler_middleware.py                  same file, generic handler
        AppError → JSON {"detail": message} + status code        logs stack trace
        RateLimitError=429 · UpstreamError=502 ·                 → 500 "Internal server error"
        NotFoundError=404 · BadRequestError=400
                         │
                         ▼
              UI shows the message in the chat panel
```

Inside the agent loop, a failing **read tool** is not fatal: the error text is sent back to Gemini as the tool result so it can adapt.

Error classes live in [core/exceptions.py](../app/core/exceptions.py).

---

## 8. How objects get wired (`core/dependencies.py`)

Created once (singletons via `lru_cache`), in this order:

```
GitHubMCPClient ──► GitHubRepository ──┐
ActionRepository ──────────────────────┼──► ApprovalService ──┐
GeminiProvider (llm_factory) ──────────┘                      ├──► ChatService ──► ChatController
GitHubRepository ─────────────────────────────────────────────┘
GitHubRepository ──► RepositoryService ──► RepositoryController
GitHubRepository ──► IssueService      ──► IssueController
ApprovalService  ──► ActionController
```

Routes receive controllers through FastAPI `Depends(get_xxx_controller)`.
To swap a part (another LLM, a database for actions), change it here and nothing else.

---

## 9. Endpoint → file cheat sheet

| Endpoint | Route | Controller | Service | Repository |
|---|---|---|---|---|
| `GET /api/health` | health_routes | (none) | (none) | (none) |
| `GET /api/meta/endpoints` | meta_routes | meta_controller | endpoint_catalog_service (reads the FastAPI route table) | (none) |
| `GET /api/repositories` | repository_routes | repository_controller | repository_service | github_repository (your GitHub repos for the dropdown) |
| `POST /api/repositories/resolve` | repository_routes | repository_controller | repository_service (+ `utils/git_url_parser.py`) | provider chosen by host |
| `GET /api/repositories/detail?repo=` | repository_routes | repository_controller | repository_service | provider |
| `GET /api/repositories/contents?repo=&path=&ref=` | repository_routes | repository_controller | repository_service | provider |
| `GET /api/repositories/file?repo=&path=&ref=` | repository_routes | repository_controller | repository_service | provider |
| `GET /api/repositories/commits?repo=` | commit_routes | commit_controller | commit_service | provider |
| `GET /api/repositories/pulls?repo=` | issue_routes | issue_controller | issue_service | provider (PRs / MRs) |
| `GET /api/repositories/{o}/{r}/issues` | issue_routes | issue_controller | issue_service | github_repository (GitHub only) |
| `POST /api/chat` | chat_routes | chat_controller | chat_service (+ llm, approval) | github_repository |
| `GET /api/actions` | action_routes | action_controller | approval_service | action_repository |
| `POST /api/actions/{id}/approve` | action_routes | action_controller | approval_service | action_repository + github_repository |
| `POST /api/actions/{id}/reject` | action_routes | action_controller | approval_service | action_repository |

---

## 10. Where do I change X?

| I want to… | Edit |
|---|---|
| Change the model or API key | `.env` (`GEMINI_MODEL`, `GEMINI_API_KEY`) |
| Use another LLM | add `llm/<name>_provider.py`, register in `llm/llm_factory.py` |
| Change how the AI behaves | `llm/prompts/repo_assistant_prompt.py` |
| Change which actions need approval | `core/config.py` → `write_tools` (rules in `mcp_layer/tool_policy.py`) |
| Change max tool rounds per question | `core/config.py` → `max_agent_rounds` |
| Use Docker MCP server instead of npx | `.env` → `GITHUB_MCP_COMMAND`, `GITHUB_MCP_ARGS` |
| Add a new endpoint | schema → service → controller → route → wire in `core/dependencies.py` |
| Store pending actions in a database | reimplement `repositories/action_repository.py` (same methods) |
| Add request auth / rate limiting | new file in `middlewares/`, register in `main.py` |

---

## 11. Multi-host support (any git link)

`repo` in every request is a repository id: `owner/name` for GitHub, `host/group/.../name` for every other host.

```
pasted link ─► utils/git_url_parser.py ─► host + repo path + (branch/file/PR the link points to)
                                              │
                                              ▼
                          providers/provider_factory.py  (chooses by host)
        ┌─────────────────────────┬──────────────────────────────┬───────────────────────────────┐
        ▼                         ▼                              ▼
 github.com                 gitlab.com / *gitlab* /        everything else: Bitbucket, Azure DevOps,
 GitHubProvider             self-hosted GitLab (probed)    Gitea, self-hosted, ssh links
 → MCP server (+ REST       GitLabProvider                 GenericGitProvider
   for metadata/images)     → GitLab REST API v4           → shallow `git clone --bare` in a cache dir
                                                             + `git ls-tree / cat-file / log`
```

| Capability | GitHub | GitLab | Other git hosts |
|---|---|---|---|
| Files, folders, branches | yes | yes | yes |
| Commits (message, author, time) | yes | yes | yes |
| Pull / merge requests | yes | yes | no (plain git has no PR data) |
| Stars, forks, description | yes | yes | no |
| AI chat | MCP tools (+ approval-gated write tools) | read-only provider tools | read-only provider tools |

Private repositories: set `GIT_HOST_TOKENS` in `.env` (host → token), or paste an `ssh://` / `git@host:` link (uses your ssh keys).

Safety of the git path (`providers/git_cli.py`): only https/http/ssh transports, no credential prompts, timeouts, size caps,
traversal and option-injection checks, and credentials are scrubbed from error messages and kept in memory only
(`repositories/repo_link_registry.py`).

Chat tool sources (`services/tool_sources.py`): `McpToolSource` for GitHub, `ProviderToolSource` (list_directory, read_file,
list_commits, list_pull_requests) for every other host.
