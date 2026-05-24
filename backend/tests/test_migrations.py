from sqlalchemy import create_engine, inspect

from app.db.migrate import run_downgrade, run_upgrade

CORE_TABLES = {"users", "prompts", "model_aliases"}


def _table_names(url: str) -> set[str]:
    engine = create_engine(url)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_upgrade_creates_all_tables(tmp_db_url: str) -> None:
    run_upgrade(tmp_db_url)
    tables = _table_names(tmp_db_url)
    assert tables >= CORE_TABLES
    assert "alembic_version" in tables


def test_downgrade_drops_all_tables(tmp_db_url: str) -> None:
    run_upgrade(tmp_db_url)
    run_downgrade(tmp_db_url, "base")
    tables = _table_names(tmp_db_url)
    assert not (CORE_TABLES & tables)


def test_upgrade_idempotent(tmp_db_url: str) -> None:
    run_upgrade(tmp_db_url)
    # Running again must be a no-op and not raise.
    run_upgrade(tmp_db_url)
    assert _table_names(tmp_db_url) >= CORE_TABLES
