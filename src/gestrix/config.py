from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Try to detect a writable base dir.
# Priority:
# 1. GESTRIX_HOME (explicit)
# 2. /app (our Docker WORKDIR)
# 3. project root (dev)
DOCKER_APP_DIR = Path("/app")
if "GESTRIX_HOME" in os.environ:
    BASE_DIR = Path(os.environ["GESTRIX_HOME"]).expanduser().resolve()
elif DOCKER_APP_DIR.exists():
    BASE_DIR = DOCKER_APP_DIR
else:
    # fallback to repo-style root (when running from source)
    BASE_DIR = Path(__file__).resolve().parents[1]

DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_PDDL_DIR = DEFAULT_DATA_DIR / "raw" / "pddl"


class Settings(BaseSettings):
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_CONFIG_FILE: str = str(BASE_DIR / "logging.ini")

    # Planner / Fast Downward
    FASTDOWNWARD_HOME: Optional[str] = os.getenv("FASTDOWNWARD_HOME")
    FD_TIMEOUT_SEC: int = 60

    # Paths (can be overridden by .env)
    DATA_DIR: str = str(DEFAULT_DATA_DIR)
    PDDL_DIR: str = str(DEFAULT_PDDL_DIR)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


def ensure_dirs() -> None:
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.PDDL_DIR).mkdir(parents=True, exist_ok=True)
