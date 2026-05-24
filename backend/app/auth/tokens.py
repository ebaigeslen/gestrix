from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.auth.schemas import TokenPayload
from app.config import Settings


class InvalidTokenError(Exception):
    """Raised when a token is missing, malformed, expired, or tampered with."""


def create_access_token(user_id: int) -> str:
    """Mint a signed JWT for `user_id` with iat/exp claims."""
    settings = Settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    claims = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT, returning its payload.

    Raises InvalidTokenError on any bad/expired/tampered/wrong-algorithm token.
    """
    settings = Settings()
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(sub=int(claims["sub"]), iat=claims["iat"], exp=claims["exp"])
    except (JWTError, KeyError, ValueError, TypeError) as exc:
        raise InvalidTokenError(str(exc)) from exc
