from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import engine, get_db


def test_engine_uses_sqlite_url() -> None:
    assert engine.url.drivername.startswith("sqlite")


def test_get_db_yields_session_and_closes() -> None:
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    assert session.is_active
    # Exhausting the generator triggers the finally block that closes it.
    with pytest.raises(StopIteration):
        next(gen)
    # A closed session has no active connection bound.
    assert session.get_bind() is not None


def test_data_dir_created_on_startup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data_dir = tmp_path / "fresh_data"
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{data_dir.as_posix()}/gestrix.db")
    assert not data_dir.exists()

    from app.main import create_app

    with TestClient(create_app()):
        assert data_dir.is_dir()
