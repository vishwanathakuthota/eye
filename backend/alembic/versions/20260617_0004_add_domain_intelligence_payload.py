from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "20260617_0004"
down_revision = "20260617_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("domain_analyses", sa.Column("intelligence", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("domain_analyses", "intelligence")


def get_revisions() -> Sequence[str]:
    return (revision,)
