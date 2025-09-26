FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2.1

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
 && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Copy dependency files first for better Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project deps (main only for runtime)
RUN pip install --no-cache-dir "poetry==" && \
    poetry config virtualenvs.create false && \
    poetry install --only main

# Copy the rest of the repo
COPY . /app

USER appuser

# Default command: run the hello CLI
CMD ["python", "-m", "gestrix.cli", "hello"]
