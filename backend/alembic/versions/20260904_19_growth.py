"""create loyalty and referral records

Revision ID: 20260904_19
Revises: 20260904_18
"""
from alembic import op
import sqlalchemy as sa
revision = "20260904_19"
down_revision = "20260904_18"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("loyalty_accounts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False), sa.Column("points", sa.Integer(), server_default="0", nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_loyalty_accounts_user_id", "loyalty_accounts", ["user_id"])
    op.create_table("loyalty_transactions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("points", sa.Integer(), nullable=False), sa.Column("event_key", sa.String(120), nullable=False), sa.Column("description", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("user_id", "event_key", name="uq_loyalty_user_event"))
    op.create_index("ix_loyalty_transactions_user_id", "loyalty_transactions", ["user_id"])
    op.create_table("referrals", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(40), nullable=False), sa.Column("referrer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("referred_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("code"), sa.UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"), sa.UniqueConstraint("referred_id"))
    op.create_index("ix_referrals_code", "referrals", ["code"]); op.create_index("ix_referrals_referrer_id", "referrals", ["referrer_id"]); op.create_index("ix_referrals_referred_id", "referrals", ["referred_id"])

def downgrade():
    op.drop_index("ix_referrals_referred_id", table_name="referrals"); op.drop_index("ix_referrals_referrer_id", table_name="referrals"); op.drop_index("ix_referrals_code", table_name="referrals"); op.drop_table("referrals"); op.drop_index("ix_loyalty_transactions_user_id", table_name="loyalty_transactions"); op.drop_table("loyalty_transactions"); op.drop_index("ix_loyalty_accounts_user_id", table_name="loyalty_accounts"); op.drop_table("loyalty_accounts")