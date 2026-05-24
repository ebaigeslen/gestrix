from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings

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
