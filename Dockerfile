FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2.1 \
    PYTHONPATH=/app/src

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
 && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Copy dependency files first for better cache
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and ONLY main deps (no project yet)
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir poetry==2.2.1 && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# Copy the rest of the repo (including src/)
COPY . /app

USER appuser

# Default command: run the hello CLI (PYTHONPATH points to /app/src)
CMD ["python", "-m", "gestrix.cli", "hello"]
