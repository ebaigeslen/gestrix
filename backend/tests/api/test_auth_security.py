import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from tests.conftest import CreatedUser

SIGNUP = "/api/auth/signup"
SIGNIN = "/api/auth/signin"
SIGNOUT = "/api/auth/signout"
ME = "/api/auth/me"


def test_password_hash_never_returned_by_any_endpoint(
    client: TestClient, test_user: CreatedUser
) -> None:
    creds = {"email": test_user.user.email, "password": test_user.password}
    responses = [
        client.post(SIGNUP, json={"email": "sweep@example.com", "password": "password123"}),
        client.post(SIGNIN, json=creds),
        client.get(ME),
        client.post(SIGNOUT),
    ]
    for resp in responses:
        assert "password_hash" not in resp.text


def test_cookie_is_httponly(client: TestClient, test_user: CreatedUser) -> None:
    resp = client.post(
        SIGNIN, json={"email": test_user.user.email, "password": test_user.password}
    )
    assert "httponly" in resp.headers["set-cookie"].lower()


def test_cookie_is_samesite_lax(client: TestClient, test_user: CreatedUser) -> None:
    resp = client.post(
        SIGNIN, json={"email": test_user.user.email, "password": test_user.password}
    )
    assert "samesite=lax" in resp.headers["set-cookie"].lower()


def test_jwt_secret_required(monkeypatch: pytest.MonkeyPatch) -> None:
    # In a non-test env with no JWT_SECRET, settings construction must fail.
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings()
