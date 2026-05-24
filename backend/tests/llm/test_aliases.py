import pytest
from sqlalchemy.orm import Session

from app.llm.aliases import list_aliases, resolve_alias
from app.llm.exceptions import AliasNotFoundError
from app.models import ModelAlias

SEED_NAMES = {
    "orchestrator",
    "writer-default",
    "namer-default",
    "keyword-default",
    "researcher-default",
    "evaluator-default",
}


def test_resolve_alias_returns_active_provider_model(db_session: Session) -> None:
    assert resolve_alias(db_session, "writer-default") == "openrouter/openai/gpt-4o"


def test_resolve_alias_unknown_raises(db_session: Session) -> None:
    with pytest.raises(AliasNotFoundError):
        resolve_alias(db_session, "does-not-exist")


def test_resolve_alias_ignores_inactive(db_session: Session) -> None:
    db_session.add(
        ModelAlias(
            alias_name="writer-default",
            version=2,
            provider_model="openrouter/other/model",
            active=False,
        )
    )
    db_session.commit()
    assert resolve_alias(db_session, "writer-default") == "openrouter/openai/gpt-4o"


def test_resolve_alias_uses_active_when_swapped(db_session: Session) -> None:
    current = db_session.query(ModelAlias).filter_by(alias_name="writer-default").one()
    current.active = False
    db_session.add(
        ModelAlias(
            alias_name="writer-default",
            version=2,
            provider_model="openrouter/anthropic/claude-3.5-sonnet",
            active=True,
        )
    )
    db_session.commit()
    assert resolve_alias(db_session, "writer-default") == "openrouter/anthropic/claude-3.5-sonnet"


def test_list_aliases_returns_six_seeded(db_session: Session) -> None:
    assert len(list_aliases(db_session)) == 6


def test_list_aliases_only_active_rows(db_session: Session) -> None:
    db_session.add(
        ModelAlias(
            alias_name="writer-default",
            version=2,
            provider_model="openrouter/other/model",
            active=False,
        )
    )
    db_session.commit()
    views = list_aliases(db_session)
    assert len(views) == 6
    assert {v.alias_name for v in views} == SEED_NAMES
