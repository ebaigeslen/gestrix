from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.password import hash_password, verify_password
from app.auth.schemas import UserResponse, UserSignin, UserSignup
from app.auth.tokens import create_access_token
from app.config import Settings
from app.db.session import get_db
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Identical message for both failure modes so signin never reveals whether an
# email exists (no user enumeration).
_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password",
)


def _set_session_cookie(response: Response, token: str) -> None:
    settings = Settings()
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_EXPIRY_MINUTES * 60,
        path="/",
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup, db: Session = Depends(get_db)) -> User:
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/signin", response_model=UserResponse)
def signin(payload: UserSignin, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise _INVALID_CREDENTIALS
    _set_session_cookie(response, create_access_token(user.id))
    return user


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
def signout(response: Response) -> None:
    settings = Settings()
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user
