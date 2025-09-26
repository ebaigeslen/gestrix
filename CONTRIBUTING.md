# Contributing

## Dev setup
- Install **Python 3.11+**.
- Install **Poetry** and keep the venv in-project:
    poetry config virtualenvs.in-project true
    poetry install --with dev
- Install git hooks:
    poetry run pre-commit install

## Useful commands
- Format:    poetry run ruff --fix .    && poetry run black .
- Lint:      poetry run ruff .          && poetry run black --check .
- Typecheck: poetry run mypy src || true
- Test:      poetry run pytest -q

## Branching & commits
- Use short feature branches: feature/..., fix/..., chore/...
- Follow Conventional Commits: feat:, fix:, docs:, chore:, refactor:, test:, ci:

## Pull request checklist
- [ ] Tests added/updated if logic changed
- [ ] poetry run pre-commit run --all-files is clean
- [ ] poetry run pytest -q passes
- [ ] Docs/README updated if needed
