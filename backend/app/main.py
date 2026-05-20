from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import Settings


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
    app.include_router(health_router)
    return app


app = create_app()
