from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_PDDL_DIR = DEFAULT_DATA_DIR / "raw" / "pddl"


class Settings(BaseSettings):
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG locally, INFO in CI/Docker
    LOG_CONFIG_FILE: str = str(ROOT_DIR / "logging.ini")

    # Planner / Fast Downward
    FASTDOWNWARD_HOME: Optional[str] = os.getenv("FASTDOWNWARD_HOME")
    FD_TIMEOUT_SEC: int = 60

    # Paths
    DATA_DIR: str = str(DEFAULT_DATA_DIR)
    PDDL_DIR: str = str(DEFAULT_PDDL_DIR)

    # Pydantic settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


# Optional helper to ensure directories exist (used by CLI or startup)
def ensure_dirs() -> None:
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.PDDL_DIR).mkdir(parents=True, exist_ok=True)
