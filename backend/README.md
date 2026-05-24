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
