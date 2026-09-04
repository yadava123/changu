"""add order item timestamp

Revision ID: 20260819_04
Revises: 20260819_03
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260819_04"
down_revision = "20260819_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("order_items")}
    if "created_at" not in columns:
        op.add_column("order_items", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE order_items SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.alter_column("created_at", nullable=False)


def downgrade() -> None:
    op.drop_column("order_items", "created_at")
