from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import ModelAlias

MODELS = "/api/models"
SEED_NAMES = {
    "orchestrator",
    "writer-default",
    "namer-default",
    "keyword-default",
    "researcher-default",
    "evaluator-default",
}


def test_get_models_requires_auth(client: TestClient) -> None:
    assert client.get(MODELS).status_code == 401


def test_get_models_returns_six_aliases(authed_client: TestClient) -> None:
    resp = authed_client.get(MODELS)
    assert resp.status_code == 200
    assert len(resp.json()) == 6


def test_get_models_response_shape(authed_client: TestClient) -> None:
    resp = authed_client.get(MODELS)
    assert resp.status_code == 200
    for item in resp.json():
        assert set(item) == {"alias_name", "provider_model", "version", "updated_at"}
    # No secrets leaked anywhere in the payload.
    assert "api_key" not in resp.text.lower()


def test_get_models_alias_names_match_spec(authed_client: TestClient) -> None:
    resp = authed_client.get(MODELS)
    assert {item["alias_name"] for item in resp.json()} == SEED_NAMES


def test_get_models_after_super_admin_swap(
    authed_client: TestClient, db_session: Session
) -> None:
    # Simulate a super-admin swap: deactivate v1, activate a v2 row.
    current = db_session.query(ModelAlias).filter_by(alias_name="orchestrator").one()
    current.active = False
    db_session.add(
        ModelAlias(
            alias_name="orchestrator",
            version=2,
            provider_model="openrouter/anthropic/claude-3.5-sonnet",
            active=True,
        )
    )
    db_session.commit()

    resp = authed_client.get(MODELS)
    assert resp.status_code == 200
    orchestrator = next(i for i in resp.json() if i["alias_name"] == "orchestrator")
    assert orchestrator["provider_model"] == "openrouter/anthropic/claude-3.5-sonnet"
    assert orchestrator["version"] == 2
