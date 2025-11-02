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
    # make sure root follows our level
    logging.getLogger().setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


@app.callback()
def main_callback() -> None:
    """Initialize logging and ensure basic directories exist."""
    _setup_logging()
    ensure_dirs()
    logging.getLogger(__name__).debug(
        "Initialized Gestrix with settings: %s", settings.model_dump()
    )


# 👇 this is the PURE function the tests expect
def hello(name: str = "world") -> str:
    """Return a greeting string (used by unit tests)."""
    return f"Hello, {name}!"


# 👇 this is the CLI command that prints
@app.command(name="hello")
def hello_cmd(name: str = typer.Argument("world", help="Name to greet")) -> None:
    """Simple sanity check command."""
    msg = hello(name)  # reuse the pure function above
    logging.getLogger(__name__).info("Hello, %s!", name)
    typer.echo(msg)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
