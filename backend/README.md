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
