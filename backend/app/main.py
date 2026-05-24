from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.config import Settings
from app.db.migrate import run_upgrade


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Ensure DATA_DIR exists and the DB is migrated to head on startup."""
    settings = Settings()
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    run_upgrade(settings.DATABASE_URL)
    yield


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(auth_router)
    return app


app = create_app()
