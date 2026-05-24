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
    # see _require_jwt_secret below.
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 10080  # 7 days
    COOKIE_NAME: str = "gestrix_session"
    COOKIE_SECURE: bool = False  # overridden to True in prod
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    @model_validator(mode="after")
    def _require_jwt_secret(self) -> "Settings":
        if not self.JWT_SECRET:
            if self.ENV != "test":
                raise ValueError("JWT_SECRET is required (set it in the environment)")
            # Tests run without a configured secret; use a fixed, clearly-insecure one.
            self.JWT_SECRET = "insecure-test-secret-do-not-use-in-prod"
        return self
