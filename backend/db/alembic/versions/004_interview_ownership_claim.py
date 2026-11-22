"""Add SQL-fenced WebSocket ownership claims.

Revision ID: 004
Revises: 003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mock_interviews",
        sa.Column("connection_state", sa.String(length=24), nullable=False, server_default="unclaimed"),
    )
    op.add_column(
        "mock_interviews",
        sa.Column("connection_generation", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("mock_interviews", sa.Column("claim_id", sa.String(length=36), nullable=True))
    op.add_column("mock_interviews", sa.Column("claim_lease_until", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_mock_interviews_connection_claim",
        "mock_interviews",
        ["connection_state", "claim_lease_until"],
    )


def downgrade() -> None:
    op.drop_index("ix_mock_interviews_connection_claim", table_name="mock_interviews")
    op.drop_column("mock_interviews", "claim_lease_until")
    op.drop_column("mock_interviews", "claim_id")
    op.drop_column("mock_interviews", "connection_generation")
    op.drop_column("mock_interviews", "connection_state")
