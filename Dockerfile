# --- builder: install deps and build wheel ---
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

COPY README.md ./
COPY src ./src

RUN poetry build -f wheel  # will create /app/dist/*.whl

# --- runtime: minimal, non-root ---
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

# create non-root user
RUN useradd -m -u 10001 appuser

# create /app and give it to appuser so it can write /app/data
WORKDIR /app
RUN mkdir -p /app && chown -R appuser:appuser /app

# install built package
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm -rf /tmp/*.whl

USER appuser

ENTRYPOINT ["python", "-m", "gestrix.cli"]
CMD []
