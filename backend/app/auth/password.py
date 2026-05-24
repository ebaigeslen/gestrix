from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if `plain` matches `hashed`.

    Returns False (never raises) for malformed/garbage hashes, so callers can
    treat any failure uniformly.
    """
    try:
        return _pwd_context.verify(plain, hashed)
    except (ValueError, TypeError):
        return False
