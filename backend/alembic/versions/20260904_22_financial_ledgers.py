"""create earnings and wallet ledgers

Revision ID: 20260904_22
Revises: 20260904_21
"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_22"
down_revision = "20260904_21"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("earning_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("gross_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("commission_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("net_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="AVAILABLE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "source_type", "source_id", name="uq_earning_source"),
    )
    op.create_index("ix_earning_records_user_id", "earning_records", ["user_id"])
    op.create_table("wallets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_wallets_user_id", "wallets", ["user_id"])
    op.create_table("wallet_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("wallet_id", sa.Integer(), sa.ForeignKey("wallets.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("transaction_type", sa.String(30), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=False),
        sa.Column("reference_type", sa.String(20), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_wallet_transaction_idempotency"),
    )
    op.create_index("ix_wallet_transactions_wallet_id", "wallet_transactions", ["wallet_id"])


def downgrade():
    op.drop_index("ix_wallet_transactions_wallet_id", table_name="wallet_transactions")
    op.drop_table("wallet_transactions")
    op.drop_index("ix_wallets_user_id", table_name="wallets")
    op.drop_table("wallets")
    op.drop_index("ix_earning_records_user_id", table_name="earning_records")
    op.drop_table("earning_records")