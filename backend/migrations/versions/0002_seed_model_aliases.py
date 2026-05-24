"""seed the 6 MVP model aliases

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# MVP defaults, frozen here to match the table in CLAUDE.md. All version=1,
# active=True. Edit live values via /admin, not by mutating this migration.
SEED_ALIASES: list[dict[str, object]] = [
    {"alias_name": "orchestrator", "provider_model": "openrouter/openai/gpt-4o-mini"},
    {"alias_name": "writer-default", "provider_model": "openrouter/openai/gpt-4o"},
    {"alias_name": "namer-default", "provider_model": "openrouter/openai/gpt-4o-mini"},
    {"alias_name": "keyword-default", "provider_model": "openrouter/openai/gpt-4o-mini"},
    {"alias_name": "researcher-default", "provider_model": "openrouter/openai/gpt-4o-mini"},
    {"alias_name": "evaluator-default", "provider_model": "openrouter/openai/gpt-4o-mini"},
]


def upgrade() -> None:
    model_aliases = sa.table(
        "model_aliases",
        sa.column("alias_name", sa.String),
        sa.column("version", sa.Integer),
        sa.column("provider_model", sa.String),
        sa.column("active", sa.Boolean),
    )
    op.bulk_insert(
        model_aliases,
        [
            {
                "alias_name": row["alias_name"],
                "version": 1,
                "provider_model": row["provider_model"],
                "active": True,
            }
            for row in SEED_ALIASES
        ],
    )


def downgrade() -> None:
    names = ", ".join(repr(row["alias_name"]) for row in SEED_ALIASES)
    op.execute(f"DELETE FROM model_aliases WHERE alias_name IN ({names})")  # noqa: S608
