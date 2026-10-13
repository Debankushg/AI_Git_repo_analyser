# GitHub Repo Assistant

An AI agent that understands a codebase and talks to GitHub through an **MCP server**.
Ask in plain English, e.g. *"Find the open bugs, pick the highest-priority one, and tell me which files need changes."*

**Stack:** React (Vite + TypeScript) · Tailwind CSS · FastAPI · Gemini API (Gemini 3.8 Flash) · GitHub MCP server

## What it does, step by step

1. **Pick a repository, or paste any git link.** The dashboard loads your GitHub repos into a selector, and you can paste a link from GitHub, GitLab, Bitbucket, Azure DevOps, Gitea or any self-hosted/ssh git URL: the host, repo, branch and file are detected automatically.
2. **Browse it.** The Repository Explorer lists files/folders (`get_file_contents`). The Issues/PR panel lists open items (`list_issues`, `list_pull_requests`).
3. **Ask a question** in the chat. The frontend sends `{repo, messages}` to `POST /api/chat`.
4. **The LLM chooses tools.** FastAPI hands Gemini the list of MCP tools. Gemini decides what it needs, e.g. `list_issues` -> `get_issue` -> `search_code` -> `get_file_contents`.
5. **Backend runs the tools.** Each tool call is forwarded to the GitHub MCP server; results go back to Gemini. This loop repeats (max 8 rounds).
6. **Gemini analyses and answers:** priority ranking, likely cause, which files probably change, a recommended fix. This appears in the chat and the AI Analysis panel.
7. **Write actions need approval.** If Gemini wants `create_issue` or `create_pull_request`, the backend does **not** run it. It stores a *pending action* and the UI shows an approval card with the exact title/body/arguments.
8. **You approve or reject.** Approve -> `POST /api/actions/{id}/approve` executes the MCP call (PRs are forced to `draft`). Reject -> discarded. Nothing is written to GitHub without your click.

```
React UI --HTTP--> FastAPI --tool loop--> Gemini API (Gemini 3.8 Flash)
                      |
                      +--stdio--> GitHub MCP server --> GitHub
```

## Folder structure

```
github-repo-assistant/
├── backend/app/
│   ├── main.py            # app factory + lifespan (starts MCP)
│   ├── core/              # config, logging, exceptions, dependencies (wiring)
│   ├── middlewares/       # request logging, error handling
│   ├── routes/            # endpoints only
│   ├── controllers/       # HTTP <-> domain adapters
│   ├── services/          # business logic + agent loop
│   ├── providers/         # one class per git host (GitHub/MCP, GitLab/REST, generic git CLI)
│   ├── repositories/      # data access (GitHub via MCP, action store)
│   ├── llm/               # provider interface, Gemini, prompts
│   ├── mcp_layer/         # client/ (MCP client), server/ (server launch config), tool_policy
│   ├── models/            # internal domain objects
│   └── schemas/           # API request/response DTOs
│   (see backend/docs/ARCHITECTURE.md for the request workflow)
├── frontend/src/
│   ├── components/{layout,repository,chat,explorer,issues,analysis,approval,common}/
│   ├── hooks/ services/ types/ pages/ utils/
└── README.md
```

Conventions: Python `snake_case.py`; React components `PascalCase.tsx`; hooks `useCamelCase.ts`; services/utils `camelCase.ts`.

## Run it

Prereqs: Python 3.11+, Node 20+, Docker (for the GitHub MCP server), a GitHub PAT, a Gemini API key.

```bash
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # fill in keys
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend && npm install && npm run dev   # http://localhost:5173
```
