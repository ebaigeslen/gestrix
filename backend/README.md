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
