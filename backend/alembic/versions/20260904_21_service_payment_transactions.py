"""add service payment transaction references

Revision ID: 20260904_21
Revises: 20260904_20
"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_21"
down_revision = "20260904_20"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_transactions") as batch:
        batch.alter_column("order_id", existing_type=sa.Integer(), nullable=True)
        batch.add_column(sa.Column("service_type", sa.String(20), nullable=False, server_default="ORDER"))
        batch.add_column(sa.Column("service_id", sa.Integer(), nullable=True))
        batch.create_index("ix_payment_transactions_service_id", ["service_id"])


def downgrade():
    with op.batch_alter_table("payment_transactions") as batch:
        batch.drop_index("ix_payment_transactions_service_id")
        batch.drop_column("service_id")
        batch.drop_column("service_type")
        batch.alter_column("order_id", existing_type=sa.Integer(), nullable=False)