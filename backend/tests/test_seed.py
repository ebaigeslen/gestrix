from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ModelAlias

# Independent copy of the spec from CLAUDE.md, so this test guards the seed
# migration against the documented MVP defaults (not against itself).
EXPECTED_ALIASES = {
    "orchestrator": "openrouter/openai/gpt-4o-mini",
    "writer-default": "openrouter/openai/gpt-4o",
    "namer-default": "openrouter/openai/gpt-4o-mini",
    "keyword-default": "openrouter/openai/gpt-4o-mini",
    "researcher-default": "openrouter/openai/gpt-4o-mini",
    "evaluator-default": "openrouter/openai/gpt-4o-mini",
}


def test_seed_inserts_six_aliases(db_session: Session) -> None:
    count = db_session.execute(select(func.count()).select_from(ModelAlias)).scalar_one()
    assert count == 6


def test_seed_alias_names_match_claude_md(db_session: Session) -> None:
    names = set(db_session.execute(select(ModelAlias.alias_name)).scalars())
    assert names == set(EXPECTED_ALIASES)


def test_seed_all_active_v1(db_session: Session) -> None:
    rows = db_session.execute(select(ModelAlias)).scalars().all()
    assert all(row.active is True for row in rows)
    assert all(row.version == 1 for row in rows)


def test_seed_provider_models_match_spec(db_session: Session) -> None:
    rows = db_session.execute(select(ModelAlias)).scalars().all()
    actual = {row.alias_name: row.provider_model for row in rows}
    assert actual == EXPECTED_ALIASES
