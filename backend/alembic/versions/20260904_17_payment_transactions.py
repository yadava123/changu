"""create payment transaction records

Revision ID: 20260904_17
Revises: 20260904_16
"""
from alembic import op
import sqlalchemy as sa
revision = "20260904_17"
down_revision = "20260904_16"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("payment_transactions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("transaction_id", sa.String(40), nullable=False), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("transaction_id"))
    op.create_index("ix_payment_transactions_transaction_id", "payment_transactions", ["transaction_id"])
    op.create_index("ix_payment_transactions_order_id", "payment_transactions", ["order_id"])
    op.create_index("ix_payment_transactions_user_id", "payment_transactions", ["user_id"])

def downgrade():
    op.drop_index("ix_payment_transactions_user_id", table_name="payment_transactions"); op.drop_index("ix_payment_transactions_order_id", table_name="payment_transactions"); op.drop_index("ix_payment_transactions_transaction_id", table_name="payment_transactions"); op.drop_table("payment_transactions")