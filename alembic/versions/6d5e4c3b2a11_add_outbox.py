"""add_outbox

Revision ID: 6d5e4c3b2a11
Revises: ccf9e766d810
Create Date: 2026-07-10 13:36:53.112000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d5e4c3b2a11"
down_revision: str | Sequence[str] | None = "ccf9e766d810"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("aggregate_id", sa.String(length=255), nullable=False),
        sa.Column("aggregate_type", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("occurred_on_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_on_utc", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("outbox")
