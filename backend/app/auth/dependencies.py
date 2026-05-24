from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.tokens import InvalidTokenError, decode_token
from app.config import Settings
from app.db.session import get_db
from app.models import User

_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Resolve the User from the session cookie, or raise 401 on any failure."""
    token = request.cookies.get(Settings().COOKIE_NAME)
    if not token:
        raise _UNAUTHENTICATED
    try:
        payload = decode_token(token)
    except InvalidTokenError:
        raise _UNAUTHENTICATED from None

    user = db.execute(select(User).where(User.id == payload.sub)).scalar_one_or_none()
    if user is None:
        raise _UNAUTHENTICATED
    return user


def get_current_super_admin(user: User = Depends(get_current_user)) -> User:
    """Require the current user to be a super admin, else raise 403."""
    if not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required",
        )
    return user
