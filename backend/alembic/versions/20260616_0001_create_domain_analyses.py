from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "20260616_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("domain", sa.String(length=253), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("dns", sa.JSON(), nullable=False),
        sa.Column("rdap", sa.JSON(), nullable=False),
        sa.Column("certificates", sa.JSON(), nullable=False),
        sa.Column("subdomains", sa.JSON(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_domain_analyses_report_id", "domain_analyses", ["report_id"], unique=True)
    op.create_index("ix_domain_analyses_domain", "domain_analyses", ["domain"])


def downgrade() -> None:
    op.drop_index("ix_domain_analyses_domain", table_name="domain_analyses")
    op.drop_index("ix_domain_analyses_report_id", table_name="domain_analyses")
    op.drop_table("domain_analyses")


def get_revisions() -> Sequence[str]:
    return (revision,)
