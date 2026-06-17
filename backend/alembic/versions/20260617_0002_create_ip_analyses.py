from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "20260617_0002"
down_revision = "20260616_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ip_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("ip", sa.String(length=45), nullable=False),
        sa.Column("ip_version", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reverse_dns", sa.JSON(), nullable=False),
        sa.Column("network", sa.JSON(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ip_analyses_report_id", "ip_analyses", ["report_id"], unique=True)
    op.create_index("ix_ip_analyses_ip", "ip_analyses", ["ip"])


def downgrade() -> None:
    op.drop_index("ix_ip_analyses_ip", table_name="ip_analyses")
    op.drop_index("ix_ip_analyses_report_id", table_name="ip_analyses")
    op.drop_table("ip_analyses")


def get_revisions() -> Sequence[str]:
    return (revision,)
