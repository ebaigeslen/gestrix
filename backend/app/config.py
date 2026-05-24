from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "gestrix-seo"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./data/gestrix.db"
    DATA_DIR: str = "./data"

    # Auth / JWT. JWT_SECRET has no real default and is REQUIRED outside tests;
    # see _require_secrets below.
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 10080  # 7 days
    COOKIE_NAME: str = "gestrix_session"
    COOKIE_SECURE: bool = False  # overridden to True in prod
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # LLM gateway (LiteLLM -> OpenRouter). OPENROUTER_API_KEY is REQUIRED outside
    # tests; see _require_secrets below.
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_DEFAULT_TIMEOUT_SECONDS: int = 60
    LLM_MAX_RETRIES: int = 2
    OPENROUTER_REFERER: str = "https://gestrix.local"
    OPENROUTER_APP_TITLE: str = "Gestrix SEO"

    @model_validator(mode="after")
    def _require_secrets(self) -> "Settings":
        # Secrets that must be provided in any real (non-test) environment.
        required = {
            "JWT_SECRET": self.JWT_SECRET,
            "OPENROUTER_API_KEY": self.OPENROUTER_API_KEY,
        }
        if self.ENV != "test":
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(
                    f"Required settings missing (set in environment): {', '.join(missing)}"
                )
        else:
            # Tests run without configured secrets; use fixed, clearly-insecure ones.
            if not self.JWT_SECRET:
                self.JWT_SECRET = "insecure-test-secret-do-not-use-in-prod"
            if not self.OPENROUTER_API_KEY:
                self.OPENROUTER_API_KEY = "test-openrouter-key"
        return self
