from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.migrate import run_downgrade, run_upgrade
from app.main import create_app


@pytest.fixture(scope="function")
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # Point the app at a throwaway DB/data dir so startup migrations never
    # touch the real ./data directory.
    data_dir = tmp_path / "data"
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{data_dir.as_posix()}/gestrix.db")
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def tmp_db_url(tmp_path: Path) -> str:
    """A file-based SQLite URL inside the test's tmp_path."""
    return f"sqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest.fixture(scope="function")
def migrated_db(tmp_db_url: str) -> Iterator[str]:
    """Run `upgrade head` on a temp DB, yield its URL, drop it on teardown."""
    run_upgrade(tmp_db_url)
    yield tmp_db_url
    run_downgrade(tmp_db_url, "base")


@pytest.fixture(scope="function")
def db_session(migrated_db: str) -> Iterator[Session]:
    """A Session bound to the migrated temp DB; rolls back on teardown."""
    engine = create_engine(migrated_db, connect_args={"check_same_thread": False})
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()
