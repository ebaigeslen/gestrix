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
