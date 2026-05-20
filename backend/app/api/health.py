from fastapi import APIRouter
from pydantic import BaseModel

from app.config import Settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = Settings()
    return HealthResponse(
        status="ok",
        service="gestrix-seo",
        version=settings.APP_VERSION,
    )
