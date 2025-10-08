# --- Builder stage: install only what's needed to build the wheel ---
FROM python:3.11-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git curl \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.8.3
WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi
COPY src ./src
RUN poetry build -f wheel

# --- Runtime stage: minimal image, non-root user, pinned python ---
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src
# Create non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app
# Install built wheel only (no dev deps)
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm -rf /tmp/*.whl
# Copy sources for CLI entry & runtime assets (owned by non-root)
COPY --chown=appuser:appuser src ./src
USER appuser
ENTRYPOINT ["python", "-m", "gestrix.cli"]
# Default prints hello; override with args as needed
CMD []
