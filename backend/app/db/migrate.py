from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import Settings

# app/db/migrate.py -> app/db -> app -> backend
BACKEND_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATIONS_DIR = BACKEND_DIR / "migrations"


def make_alembic_config(url: str) -> Config:
    """Build an Alembic Config pointing at this project's migrations + URL."""
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def run_upgrade(url: str | None = None) -> None:
    """Run `alembic upgrade head` programmatically against `url`."""
    resolved = url or Settings().DATABASE_URL
    command.upgrade(make_alembic_config(resolved), "head")


def run_downgrade(url: str, revision: str = "base") -> None:
    """Run `alembic downgrade <revision>` programmatically against `url`."""
    command.downgrade(make_alembic_config(url), revision)
