import os

# Must be set before app modules construct Settings(). ENV=test relaxes the
# JWT_SECRET requirement; we still pin a fixed secret so tokens are stable.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-key-not-for-prod")

from collections.abc import Iterator  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import NamedTuple  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import Engine, create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.auth.password import hash_password  # noqa: E402
from app.db.migrate import run_downgrade, run_upgrade  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import User  # noqa: E402


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
def db_engine(migrated_db: str) -> Iterator[Engine]:
    """A single engine bound to the migrated temp DB, shared by db_session + client."""
    engine = create_engine(migrated_db, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Iterator[Session]:
    """A Session on the migrated temp DB; rolls back on teardown."""
    factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(
    db_engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """TestClient whose get_db dependency is bound to the same migrated temp DB.

    Lifespan migrations are pointed at the same DB file (idempotent) and a tmp
    DATA_DIR, so startup never touches the real ./data directory.
    """
    monkeypatch.setenv("DATABASE_URL", str(db_engine.url))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_get_db() -> Iterator[Session]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class CreatedUser(NamedTuple):
    user: User
    password: str


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> CreatedUser:
    password = "password123"
    user = User(email="user@example.com", password_hash=hash_password(password))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return CreatedUser(user=user, password=password)


@pytest.fixture(scope="function")
def super_admin_user(db_session: Session) -> CreatedUser:
    password = "adminpass123"
    user = User(
        email="admin@example.com",
        password_hash=hash_password(password),
        is_super_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return CreatedUser(user=user, password=password)


@pytest.fixture(scope="function")
def authed_client(client: TestClient, test_user: CreatedUser) -> TestClient:
    resp = client.post(
        "/api/auth/signin",
        json={"email": test_user.user.email, "password": test_user.password},
    )
    assert resp.status_code == 200
    return client


@pytest.fixture(scope="function")
def super_admin_client(client: TestClient, super_admin_user: CreatedUser) -> TestClient:
    resp = client.post(
        "/api/auth/signin",
        json={"email": super_admin_user.user.email, "password": super_admin_user.password},
    )
    assert resp.status_code == 200
    return client


@pytest.fixture(scope="function")
def mock_litellm(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch `litellm.completion`; tests set `.return_value` / `.side_effect`."""
    mock = MagicMock()
    monkeypatch.setattr("litellm.completion", mock)
    return mock
