from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.exceptions import AliasNotFoundError
from app.models import ModelAlias


class ModelAliasView(BaseModel):
    """Public view of an active model alias (no provider keys, no internal ids)."""

    model_config = ConfigDict(from_attributes=True)

    alias_name: str
    provider_model: str
    version: int
    updated_at: datetime


def resolve_alias(db: Session, alias_name: str) -> str:
    """Return the active provider_model for `alias_name`.

    Raises AliasNotFoundError if no active row exists for that alias.
    """
    provider_model = db.execute(
        select(ModelAlias.provider_model).where(
            ModelAlias.alias_name == alias_name,
            ModelAlias.active.is_(True),
        )
    ).scalar_one_or_none()
    if provider_model is None:
        raise AliasNotFoundError(f"No active model alias named {alias_name!r}")
    return provider_model


def list_aliases(db: Session) -> list[ModelAliasView]:
    """Return a view of every active model alias (one SELECT, no N+1)."""
    rows = db.execute(
        select(ModelAlias).where(ModelAlias.active.is_(True)).order_by(ModelAlias.alias_name)
    ).scalars()
    return [ModelAliasView.model_validate(row) for row in rows]
