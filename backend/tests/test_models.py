import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import ModelAlias, Prompt, User


def test_user_create_and_query(db_session: Session) -> None:
    db_session.add(User(email="a@example.com", password_hash="hash"))
    db_session.commit()

    user = db_session.execute(
        select(User).where(User.email == "a@example.com")
    ).scalar_one()
    assert user.id is not None
    assert user.is_super_admin is False
    assert user.created_at is not None


def test_user_email_unique(db_session: Session) -> None:
    db_session.add(User(email="dup@example.com", password_hash="h1"))
    db_session.commit()
    db_session.add(User(email="dup@example.com", password_hash="h2"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_prompt_unique_agent_version(db_session: Session) -> None:
    db_session.add(Prompt(agent_name="writer", version=1, body="b1"))
    db_session.commit()
    db_session.add(Prompt(agent_name="writer", version=1, body="b2"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_prompt_only_one_active_per_agent(db_session: Session) -> None:
    db_session.add(Prompt(agent_name="writer", version=1, body="b1", active=True))
    db_session.commit()
    db_session.add(Prompt(agent_name="writer", version=2, body="b2", active=True))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_model_alias_unique_alias_version(db_session: Session) -> None:
    db_session.add(
        ModelAlias(alias_name="custom", version=1, provider_model="openrouter/x")
    )
    db_session.commit()
    db_session.add(
        ModelAlias(alias_name="custom", version=1, provider_model="openrouter/y")
    )
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_model_alias_only_one_active_per_alias(db_session: Session) -> None:
    db_session.add(
        ModelAlias(
            alias_name="custom", version=1, provider_model="openrouter/x", active=True
        )
    )
    db_session.commit()
    db_session.add(
        ModelAlias(
            alias_name="custom", version=2, provider_model="openrouter/y", active=True
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
