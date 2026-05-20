from fastapi.testclient import TestClient

from app.config import Settings


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_response_shape(client: TestClient) -> None:
    response = client.get("/api/health")
    assert set(response.json().keys()) == {"status", "service", "version"}


def test_health_status_is_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.json()["status"] == "ok"


def test_health_service_name(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.json()["service"] == "gestrix-seo"


def test_health_version_matches_settings(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.json()["version"] == Settings().APP_VERSION
