from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.llm.aliases import ModelAliasView, list_aliases
from app.models import User

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[ModelAliasView])
def get_models(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[ModelAliasView]:
    """List all active model aliases. Requires authentication."""
    return list_aliases(db)
