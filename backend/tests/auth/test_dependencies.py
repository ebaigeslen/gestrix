import time

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.auth.dependencies import get_current_super_admin, get_current_user
from app.auth.password import hash_password
from app.auth.tokens import create_access_token
from app.config import Settings
from app.models import User

COOKIE_NAME = Settings().COOKIE_NAME


def _request(cookie_value: str | None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if cookie_value is not None:
        headers.append((b"cookie", f"{COOKIE_NAME}={cookie_value}".encode()))
    return Request({"type": "http", "headers": headers})


def _make_user(db: Session, *, is_super_admin: bool = False) -> User:
    user = User(
        email="dep@example.com",
        password_hash=hash_password("password123"),
        is_super_admin=is_super_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_get_current_user_no_cookie_401(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc:
        get_current_user(_request(None), db_session)
    assert exc.value.status_code == 401


def test_get_current_user_invalid_cookie_401(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc:
        get_current_user(_request("garbage.token.value"), db_session)
    assert exc.value.status_code == 401


def test_get_current_user_expired_cookie_401(db_session: Session) -> None:
    settings = Settings()
    now = int(time.time())
    token = jwt.encode(
        {"sub": "1", "iat": now - 100, "exp": now - 10},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc:
        get_current_user(_request(token), db_session)
    assert exc.value.status_code == 401


def test_get_current_user_valid_cookie_returns_user(db_session: Session) -> None:
    user = _make_user(db_session)
    result = get_current_user(_request(create_access_token(user.id)), db_session)
    assert result.id == user.id


def test_get_current_user_user_deleted_after_token_issued_401(db_session: Session) -> None:
    user = _make_user(db_session)
    token = create_access_token(user.id)
    db_session.delete(user)
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        get_current_user(_request(token), db_session)
    assert exc.value.status_code == 401


def test_get_current_super_admin_regular_user_403(db_session: Session) -> None:
    user = _make_user(db_session, is_super_admin=False)
    with pytest.raises(HTTPException) as exc:
        get_current_super_admin(user)
    assert exc.value.status_code == 403


def test_get_current_super_admin_super_admin_returns_user(db_session: Session) -> None:
    user = _make_user(db_session, is_super_admin=True)
    assert get_current_super_admin(user).id == user.id
