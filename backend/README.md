# Gestrix Backend

FastAPI backend for Gestrix SEO.

## Setup

```bash
uv sync
```

## Run dev server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
uv run pytest
```

## Lint

```bash
uv run ruff check .
```

## Type-check

```bash
uv run mypy app
```

## Database

The backend uses SQLite (via SQLAlchemy 2.0) with Alembic migrations. The DB
URL comes from `app.config.Settings.DATABASE_URL` (default
`sqlite:///./data/gestrix.db`); `migrations/env.py` reads it from there.

The app auto-runs `alembic upgrade head` on startup (and creates `DATA_DIR`),
so a fresh dev or Docker boot always gets a ready, migrated database with no
manual steps.

Manual migration commands (run from `backend/`):

```bash
# Apply all migrations
uv run alembic upgrade head

# Roll back the most recent migration
uv run alembic downgrade -1

# Generate a new migration from model changes
uv run alembic revision --autogenerate -m "msg"
```

## Auth

Cookie-based authentication: passwords are bcrypt-hashed (via passlib) and the
session is a JWT carried in an **HttpOnly** cookie (`gestrix_session`,
`SameSite=lax`, `Secure` in prod). `JWT_SECRET` is **required** in any non-test
environment — settings construction fails without it (see `.env.example`).

Endpoints (all under `/api/auth`):

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| POST | `/signup` | none | `201` `UserResponse` | `409` email exists · `422` invalid email / password < 8 |
| POST | `/signin` | none | `200` `UserResponse` + sets cookie | `401` invalid email **or** password (identical message) |
| POST | `/signout` | none | `204`, clears cookie | — |
| GET | `/me` | cookie | `200` `UserResponse` | `401` missing/expired/tampered cookie |

`UserResponse` is `{id, email, is_super_admin, created_at}` — it never includes
`password_hash`.

Two FastAPI dependencies protect downstream routes:

```python
from app.auth.dependencies import get_current_user, get_current_super_admin

@router.get("/something")
def handler(user: User = Depends(get_current_user)): ...        # 401 if not signed in

@router.get("/admin-only")
def admin(user: User = Depends(get_current_super_admin)): ...    # 403 if not super admin
```

## LLM

All LLM calls go through **LiteLLM pointed at OpenRouter**, behind one funnel in
`app/llm/`. Agents never see a provider model string — they reference an
**alias** (e.g. `writer-default`), which is resolved to the active
`provider_model` from the `model_aliases` table at call time. Super admin can
swap an alias's model (insert a new active row) with no redeploy.

```python
from app.db.session import SessionLocal
from app.llm.client import chat_completion, chat_completion_structured

with SessionLocal() as db:
    # Plain chat completion — returns the raw LiteLLM response.
    resp = chat_completion(db, "writer-default",
                           [{"role": "user", "content": "Write a tagline."}])
    text = resp["choices"][0]["message"]["content"]

    # Structured output — parsed into a Pydantic model.
    result = chat_completion_structured(db, "writer-default", messages, MySchema)
```

Errors are normalized: `AliasNotFoundError` (no active alias),
`LLMCallError` (provider/network failure, wraps the cause),
`LLMStructuredOutputError` (response didn't parse). All extend `LLMError`.

`GET /api/models` (auth required) returns the active aliases as
`{alias_name, provider_model, version, updated_at}` — never any keys.

**Two hard rules (enforced by `tests/llm/test_guardrails.py`):**
1. Only `app/llm/client.py` may import `litellm`.
2. No raw `openrouter/...` model strings anywhere outside the `model_aliases`
   table — reference models by alias.

Settings: `OPENROUTER_API_KEY` is **required** outside tests; plus
`OPENROUTER_BASE_URL`, `LLM_DEFAULT_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES`,
`OPENROUTER_REFERER`, `OPENROUTER_APP_TITLE` (see `.env.example`).

The live OpenRouter test is marked `integration` and skipped by default; run it
with a real key via `uv run pytest -m integration`.
