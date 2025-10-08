from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import typer

from gestrix.config import settings, ensure_dirs

app = typer.Typer(help="Gestrix — Neuro-symbolic planning toolkit")


def _setup_logging() -> None:
    cfg = Path(settings.LOG_CONFIG_FILE)
    if cfg.exists():
        logging.config.fileConfig(cfg, disable_existing_loggers=False)
    # Ensure the root logger level follows settings (overrides file level)
    logging.getLogger().setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


@app.callback()
def main_callback() -> None:
    """Initialize logging and ensure basic directories exist."""
    _setup_logging()
    ensure_dirs()
    logging.getLogger(__name__).debug(
        "Initialized Gestrix with settings: %s", settings.model_dump()
    )


@app.command()
def hello(name: str = typer.Argument("world", help="Name to greet")) -> None:
    """Simple sanity check command."""
    logging.getLogger(__name__).info("Hello, %s!", name)
    typer.echo(f"Hello, {name}!")


if __name__ == "__main__":
    app()
