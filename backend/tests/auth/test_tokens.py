import time

import pytest
from jose import jwt

from app.auth.tokens import InvalidTokenError, create_access_token, decode_token
from app.config import Settings


def test_create_and_decode_roundtrip() -> None:
    payload = decode_token(create_access_token(42))
    assert payload.sub == 42


def test_token_has_exp_in_future() -> None:
    payload = decode_token(create_access_token(1))
    assert payload.exp > int(time.time())


def test_decode_expired_token_raises() -> None:
    settings = Settings()
    now = int(time.time())
    token = jwt.encode(
        {"sub": "1", "iat": now - 100, "exp": now - 10},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token)


def test_decode_tampered_signature_raises() -> None:
    token = create_access_token(7)
    # Flip the last character of the signature segment.
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(InvalidTokenError):
        decode_token(tampered)


def test_decode_wrong_algorithm_raises() -> None:
    settings = Settings()
    now = int(time.time())
    # Signed with HS512 instead of the expected HS256.
    token = jwt.encode(
        {"sub": "1", "iat": now, "exp": now + 100},
        settings.JWT_SECRET,
        algorithm="HS512",
    )
    with pytest.raises(InvalidTokenError):
        decode_token(token)
