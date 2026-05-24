from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserSignin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    # from_attributes lets us build this straight from a SQLAlchemy User row.
    # It only declares safe fields, so password_hash can never be serialized.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_super_admin: bool
    created_at: datetime


class TokenPayload(BaseModel):
    sub: int
    iat: int
    exp: int
