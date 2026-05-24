# Gestrix SEO Project

## Overview

Gestrix SEO is a SaaS product that lets users generate top-tier, SEO-optimized product descriptions (and later: blog posts, tags, product names, internal links) through an AI agent team.

The user opens a chat, optionally provides a product name / keywords / niche / writing style / sample structure / focus keyword / external links to reference, and selects a skill. The orchestrator agent routes the request through a team of sub-agents (Writer, optional Naming, optional Keyword, optional Deep Research) to produce a finished description with a live preview alongside the chat.


MVP supports one skill — `product-description-writer`. Blog post writer, tag generator, and internal-linker land in later phases.

## Development process

When instructed to build a feature:
1. Use your Atlassian tools to read the feature instructions from Jira
2. Develop the feature — do not skip any step from the feature-dev 7-step process
3. Thoroughly test the feature with unit tests and integration tests, and fix any issues
4. Submit a PR using your github tools

## AI design

When writing code that calls LLMs:
- Never call a provider SDK (`openai`, `anthropic`, `google-genai`) directly.
- Always call **LiteLLM** pointed at **OpenRouter**. This is the only place that knows about specific providers.
- **Every agent has its own model alias. There is no global model.** The orchestrator and every sub-agent are swappable independently. Super admin can assign a different OpenRouter model to each one.
- Aliases live in the **`model_aliases` SQLite table** (not a YAML file) so super admin can swap any agent's model from the `/admin` UI with zero redeploy.
- Aliases are **versioned** — one `active=true` row per alias name. Rollback is one click.
- Use **Structured Outputs** (Pydantic models) for every agent so handoffs are typed and field extraction is reliable.
- Agent orchestration uses **Pydantic AI** — its `Agent` class points at the LiteLLM-via-OpenRouter base URL and never knows the underlying provider.

### MVP aliases (each independently editable in `/admin/models`)

| Alias | MVP default | Used by | Phase |
|---|---|---|---|
| `orchestrator` | `openrouter/openai/gpt-4o-mini` | Orchestrator (routing / handoff decisions) | GS-E0 |
| `writer-default` | `openrouter/openai/gpt-4o` | Writer agent | GS-E1 |
| `namer-default` | `openrouter/openai/gpt-4o-mini` | Naming agent | GS-E2 |
| `keyword-default` | `openrouter/openai/gpt-4o-mini` | Keyword agent | GS-E2 |
| `researcher-default` | `openrouter/openai/gpt-4o-mini` | Deep Research agent | GS-E4 |
| `evaluator-default` | `openrouter/openai/gpt-4o-mini` | Evaluator agent | GS-E4 |

To swap any agent's model: super admin opens `/admin/models`, picks the alias, chooses a new OpenRouter model string, saves. Effective on the next request.

There is an `OPENROUTER_API_KEY` in the `.env` file in the project root. Optional keys (`TAVILY_API_KEY`, `LOGFIRE_TOKEN`) are documented in `.env.example`.

## Prompts

- **No prompt is ever hardcoded in Python.** All prompts live in the `prompts` SQLite table.
- Each agent reads its active prompt at request time. Super admin edits and versions prompts in the `/admin` UI.
- Schema: `prompts(id, agent_name, version, body, active, created_by, created_at)`. Exactly one row per `agent_name` has `active=true`.
- To draft/promote prompts in dev, use slash commands: `/new-prompt <agent>` and `/promote-prompt <agent> <version>`.

## Agent team

| Agent | MVP? | Role |
|---|---|---|
| `Orchestrator` | yes | Routes the user request, decides which sub-agents to call, manages handoffs |
| `Writer` | yes | Produces the final product description from all gathered context |
| `Naming` | optional in MVP | Generates a product name only if the user didn't provide one |
| `Keyword` | optional in MVP | Finds focus keyword + semantics only if the user didn't provide them |
| `Researcher` | phase 2 | Tavily-powered deep research, toggle in chat |
| `Evaluator` | phase 2 | Scores Writer output against a rubric, triggers one revision pass |

Input validation is a **Pydantic schema**, not an agent. Don't burn tokens on what a schema can do.

## Technical design

The entire project is packaged into a Docker container.
The backend is in `backend/` and is a `uv` project, using FastAPI + Pydantic AI.
The frontend is in `frontend/` (Next.js 15 + Vercel AI SDK + shadcn/ui).
The database uses SQLite and is created from scratch each time the Docker container is brought up, with the following tables: `users`, `prompts`, `chats`, `messages`, `runs`, `agent_traces`, `documents`, `api_keys` (encrypted, for future BYO-key feature).
The Next.js frontend is **statically built and served by FastAPI** so there is one process and one port.

Scripts in `scripts/` for:

```bash
```

## Implementation status

### GES-2 — FastAPI backend bootstrap — Done 2026-05-20

- PR [#4](https://github.com/ebaigeslen/gestrix/pull/4) (squash `cff82d6`)
- `backend/` is a `uv` project on Python 3.12 (pinned via `backend/.python-version`). Runtime deps: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`. Dev deps: `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`. `uv.lock` committed.
- `backend/app/main.py` — `create_app()` factory + module-level `app = create_app()`.
- `backend/app/config.py` — `Settings` (pydantic-settings) with `APP_NAME`, `APP_VERSION`, `ENV`.
- `backend/app/api/health.py` — `GET /api/health` → `200 {"status":"ok","service":"gestrix-seo","version":"<APP_VERSION>"}`.
- 9 tests in `backend/tests/` (5 health, 2 config, 2 factory) + function-scoped `client` fixture in `conftest.py`.
- Dev loop (run from `backend/`):
  ```bash
  uv sync
  uv run uvicorn app.main:app --reload --port 8000
  uv run pytest
  uv run ruff check .
  uv run mypy app
  ```
- Ruff config: `select = ["E","F","W","I","UP","B","SIM"]`, line-length 100. Mypy: `strict = true`, scoped to `app/`.
- `.gitignore` has `!backend/.python-version` so the Python pin is tracked.
- **Not built yet (out of scope for GES-2):** SQLite tables, agents, LiteLLM/OpenRouter wiring, frontend, Docker, `/admin`, auth.

### GES-3 — SQLite + Alembic schema (users, prompts, model_aliases) + seeded aliases — Done 2026-05-24

- PR [#5](https://github.com/ebaigeslen/gestrix/pull/5) (branch `feat/ges-2-db-and-schema`)
- SQLAlchemy 2.0 + Alembic added. Runtime deps: `sqlalchemy>=2.0`, `alembic`, `aiosqlite` (kept for future async, currently unused), `passlib[bcrypt]` (placeholder for auth). Dev dep: `pytest-cov`.
- `backend/app/config.py` adds `DATABASE_URL` (default `sqlite:///./data/gestrix.db`) and `DATA_DIR` (default `./data`).
- `backend/app/db/` — `base.py` (`Base(DeclarativeBase)`), `session.py` (`engine`, `SessionLocal`, `get_db()` — **sync** Session), `migrate.py` (`run_upgrade` / `run_downgrade` programmatic helpers).
- `backend/app/models/` — `User`, `Prompt`, `ModelAlias`. Each of prompts/model_aliases has a `(name, version)` unique constraint **and a partial unique index `WHERE active = 1`** — the "at most one active row per name" invariant is enforced in the schema, not app code.
- `backend/migrations/` — Alembic env reads the URL from `Settings`; `0001_initial_schema` creates the 3 tables, `0002_seed_model_aliases` seeds the 6 MVP aliases (all `version=1`, `active=True`). `alembic.ini` deliberately has **no `sqlalchemy.url`** — `env.py` is the single source of truth.
- `backend/app/main.py` lifespan ensures `DATA_DIR` exists and runs `alembic upgrade head` on startup, so dev/Docker boots a ready DB with no manual steps.
- DB commands (run from `backend/`): `uv run alembic upgrade head`, `uv run alembic downgrade -1`, `uv run alembic revision --autogenerate -m "msg"`. Documented in `backend/README.md`.
- 25 tests (was 9): added `test_db_session`, `test_models`, `test_migrations`, `test_seed` + `conftest` fixtures `tmp_db_url` / `migrated_db` / `db_session`. 100% coverage on `app/models/` and `app/db/`.
- `.gitignore` excludes `backend/data/` (DB created at runtime, never committed).
- **Not built yet (out of scope for GES-3):** auth logic, `/admin`, prompt/alias CRUD endpoints, LiteLLM/OpenRouter wiring, the remaining tables (`chats`, `messages`, `runs`, `agent_traces`, `documents`, `api_keys`), frontend, Docker.

### GES-4 — User authentication (signup/signin/signout/me, bcrypt + JWT cookie) — Done 2026-05-24

- PR [#6](https://github.com/ebaigeslen/gestrix/pull/6) (squash `b46ca1a`), branch `feat/ges-4-auth`. `/security-review` run on the diff — clean, no findings.
- Cookie-based auth: bcrypt password hashing (passlib) + JWT in an **HttpOnly**, `SameSite=lax` cookie (`gestrix_session`; `Secure` in prod).
- `backend/app/config.py` adds `JWT_SECRET` (**required outside tests** — `model_validator` raises if missing when `ENV != "test"`), `JWT_ALGORITHM` (`HS256`), `JWT_EXPIRY_MINUTES` (10080 / 7 days), `COOKIE_NAME`, `COOKIE_SECURE`, `COOKIE_SAMESITE`. Root `.env.example` documents all settings.
- `backend/app/auth/` — `password.py` (`hash_password` / `verify_password`, returns False on garbage hash), `tokens.py` (`create_access_token` / `decode_token` → `TokenPayload`, raising `InvalidTokenError`; decode pins `algorithms=[HS256]`), `dependencies.py` (`get_current_user` → 401, `get_current_super_admin` → 403), `schemas.py` (Pydantic; `UserResponse` is a field allowlist that can never serialize `password_hash`).
- `backend/app/api/auth.py` — `POST /api/auth/signup` (201/409/422), `signin` (200 + cookie / 401 identical message → no user enumeration), `signout` (204, clears cookie), `GET /me` (200/401). Router tag `auth`, wired in `main.py`.
- Protect future routes with `user: User = Depends(get_current_user)` (or `get_current_super_admin`).
- Deps added: `python-jose[cryptography]`, `email-validator`; **`bcrypt` pinned `>=4.0,<4.1`** (passlib 1.7.4 is incompatible with bcrypt 5.0). Dev: `types-passlib`, `types-python-jose`. Ruff `flake8-bugbear.extend-immutable-calls` lets FastAPI `Depends()` defaults pass.
- 61 tests (was 25): `tests/auth/{test_password,test_tokens,test_dependencies}` + `tests/api/{test_auth_endpoints,test_auth_security}` + conftest fixtures `test_user` / `super_admin_user` / `authed_client` / `super_admin_client`. The `client` fixture now overrides `get_db` onto the same migrated temp DB as `db_session`. 100% coverage on `app/auth/`.
- **Not built yet (out of scope for GES-4):** server-side token revocation/denylist, `/admin`, prompt/alias CRUD, LiteLLM/OpenRouter wiring, the remaining tables, frontend, Docker.