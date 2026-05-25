import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AgentTrace, Chat, Document, Message, Run, User


def _make_chat(db: Session) -> Chat:
    user = User(email="chat@example.com", password_hash="h")
    db.add(user)
    db.commit()
    chat = Chat(user_id=user.id, title="My product")
    db.add(chat)
    db.commit()
    return chat


def test_chat_create_and_query(db_session: Session) -> None:
    chat = _make_chat(db_session)
    assert chat.id is not None
    assert chat.created_at is not None
    assert chat.updated_at is not None


def test_chat_title_optional(db_session: Session) -> None:
    user = User(email="notitle@example.com", password_hash="h")
    db_session.add(user)
    db_session.commit()
    chat = Chat(user_id=user.id)
    db_session.add(chat)
    db_session.commit()
    assert chat.title is None


def test_run_defaults_to_pending(db_session: Session) -> None:
    chat = _make_chat(db_session)
    run = Run(chat_id=chat.id, skill="product-description-writer")
    db_session.add(run)
    db_session.commit()
    assert run.status == "pending"
    assert run.completed_at is None


def test_message_role_check_constraint(db_session: Session) -> None:
    chat = _make_chat(db_session)
    db_session.add(Message(chat_id=chat.id, role="robot", content="hi"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_run_status_check_constraint(db_session: Session) -> None:
    chat = _make_chat(db_session)
    db_session.add(Run(chat_id=chat.id, skill="x", status="bogus"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_invalid_chat_fk_rejected(db_session: Session) -> None:
    # Confirms FK enforcement is actually ON (SQLite ignores FKs by default).
    db_session.add(Message(chat_id=999_999, role="user", content="orphan"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_agent_trace_json_roundtrip(db_session: Session) -> None:
    chat = _make_chat(db_session)
    run = Run(chat_id=chat.id, skill="product-description-writer")
    db_session.add(run)
    db_session.commit()
    db_session.add(
        AgentTrace(
            run_id=run.id,
            agent_name="writer",
            model_alias="writer-default",
            input_json={"prompt": "hi", "opts": [1, 2]},
            output_json={"text": "ok", "nested": {"k": True}},
        )
    )
    db_session.commit()
    trace = db_session.execute(select(AgentTrace)).scalar_one()
    assert trace.input_json == {"prompt": "hi", "opts": [1, 2]}
    assert trace.output_json == {"text": "ok", "nested": {"k": True}}
    assert trace.prompt_tokens is None


def test_delete_chat_cascades_children(db_session: Session) -> None:
    chat = _make_chat(db_session)
    db_session.add_all(
        [
            Message(chat_id=chat.id, role="user", content="hi"),
            Run(chat_id=chat.id, skill="product-description-writer"),
            Document(chat_id=chat.id, kind="product_description", content="desc"),
        ]
    )
    db_session.commit()

    db_session.delete(chat)
    db_session.commit()

    for model in (Message, Run, Document):
        count = db_session.execute(select(func.count()).select_from(model)).scalar_one()
        assert count == 0, f"{model.__name__} rows should be cascade-deleted"


def test_delete_run_cascades_traces(db_session: Session) -> None:
    chat = _make_chat(db_session)
    run = Run(chat_id=chat.id, skill="product-description-writer")
    db_session.add(run)
    db_session.commit()
    db_session.add(
        AgentTrace(
            run_id=run.id,
            agent_name="writer",
            model_alias="writer-default",
            input_json={},
        )
    )
    db_session.commit()

    db_session.delete(run)
    db_session.commit()

    count = db_session.execute(select(func.count()).select_from(AgentTrace)).scalar_one()
    assert count == 0
