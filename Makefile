SHELL := /bin/bash

.PHONY: setup lint format test run build clean

setup:
	poetry install --with dev

lint:
	poetry run ruff .
	poetry run black --check .
	poetry run mypy src || true

format:
	poetry run ruff --fix .
	poetry run black .

test:
	poetry run pytest -q

run:
	poetry run python -m gestrix.cli hello

build:
	poetry build

clean:
	rm -rf dist .pytest_cache .ruff_cache .mypy_cache
# --- Docker targets (Day 2) ---
DOCKER_IMAGE ?= gestrix:dev
DOCKER_BUILD_ARGS ?=
.PHONY: docker-build docker-run

docker-build:
    DOCKER_BUILDKIT=1 docker build $(DOCKER_BUILD_ARGS) -t $(DOCKER_IMAGE) .

docker-run:
    docker run --rm $(DOCKER_IMAGE)
preview-data:
    python scripts/check_pddl_syntax.py
