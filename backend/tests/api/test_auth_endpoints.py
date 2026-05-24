from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import verify_password
from app.models import User
from tests.conftest import CreatedUser

SIGNUP = "/api/auth/signup"
SIGNIN = "/api/auth/signin"
SIGNOUT = "/api/auth/signout"
ME = "/api/auth/me"


def test_signup_happy_path(client: TestClient) -> None:
    resp = client.post(SIGNUP, json={"email": "new@example.com", "password": "password123"})
    assert resp.status_code == 201
    body = resp.json()
    assert set(body) == {"id", "email", "is_super_admin", "created_at"}
    assert body["email"] == "new@example.com"
    assert body["is_super_admin"] is False
    assert "password_hash" not in body


def test_signup_duplicate_email_409(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post(SIGNUP, json=payload).status_code == 201
    assert client.post(SIGNUP, json=payload).status_code == 409


def test_signup_invalid_email_422(client: TestClient) -> None:
    resp = client.post(SIGNUP, json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422


def test_signup_short_password_422(client: TestClient) -> None:
    resp = client.post(SIGNUP, json={"email": "short@example.com", "password": "1234567"})
    assert resp.status_code == 422


def test_signup_stores_bcrypt_hash(client: TestClient, db_session: Session) -> None:
    client.post(SIGNUP, json={"email": "hash@example.com", "password": "password123"})
    user = db_session.execute(
        select(User).where(User.email == "hash@example.com")
    ).scalar_one()
    assert user.password_hash != "password123"
    assert verify_password("password123", user.password_hash) is True


def test_signin_happy_path_sets_cookie(client: TestClient, test_user: CreatedUser) -> None:
    resp = client.post(
        SIGNIN, json={"email": test_user.user.email, "password": test_user.password}
    )
    assert resp.status_code == 200
    set_cookie = resp.headers["set-cookie"].lower()
    assert "gestrix_session=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie


def test_signin_wrong_password_401(client: TestClient, test_user: CreatedUser) -> None:
    resp = client.post(
        SIGNIN, json={"email": test_user.user.email, "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_signin_nonexistent_user_401(client: TestClient) -> None:
    resp = client.post(SIGNIN, json={"email": "ghost@example.com", "password": "password123"})
    assert resp.status_code == 401


def test_signin_error_messages_identical(client: TestClient, test_user: CreatedUser) -> None:
    wrong_pw = client.post(
        SIGNIN, json={"email": test_user.user.email, "password": "wrong-password"}
    )
    nonexistent = client.post(
        SIGNIN, json={"email": "ghost@example.com", "password": "password123"}
    )
    assert wrong_pw.status_code == nonexistent.status_code == 401
    # Byte-identical bodies — no way to tell which factor failed.
    assert wrong_pw.content == nonexistent.content


def test_signout_clears_cookie(authed_client: TestClient) -> None:
    resp = authed_client.post(SIGNOUT)
    assert resp.status_code == 204
    assert "max-age=0" in resp.headers["set-cookie"].lower()


def test_signout_without_session_still_204(client: TestClient) -> None:
    assert client.post(SIGNOUT).status_code == 204


def test_me_with_valid_cookie_returns_user(
    authed_client: TestClient, test_user: CreatedUser
) -> None:
    resp = authed_client.get(ME)
    assert resp.status_code == 200
    assert resp.json()["email"] == test_user.user.email


def test_me_without_cookie_401(client: TestClient) -> None:
    assert client.get(ME).status_code == 401


def test_me_after_signout_401(authed_client: TestClient) -> None:
    assert authed_client.get(ME).status_code == 200
    authed_client.post(SIGNOUT)
    assert authed_client.get(ME).status_code == 401


def test_me_response_excludes_password_hash(authed_client: TestClient) -> None:
    resp = authed_client.get(ME)
    assert "password_hash" not in resp.text
