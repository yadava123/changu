"""set order item timestamp default

Revision ID: 20260819_05
Revises: 20260819_04
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260819_05"
down_revision = "20260819_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.alter_column("created_at", server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.alter_column("created_at", server_default=None)
