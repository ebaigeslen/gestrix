from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
    """SQLite ignores foreign keys unless told otherwise. Enable enforcement
    (so ON DELETE CASCADE works) on every connection, app and tests alike.
    Registered on the Engine class so any engine built from this process gets it.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


settings = Settings()

# check_same_thread=False is required for SQLite under FastAPI's threaded
# request handling (and the threaded TestClient).
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a Session, closed on request teardown."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
