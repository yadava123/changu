"""create coupon and usage records

Revision ID: 20260904_18
Revises: 20260904_17
"""
from alembic import op
import sqlalchemy as sa
revision = "20260904_18"
down_revision = "20260904_17"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("coupons", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(40), nullable=False), sa.Column("discount_percent", sa.Numeric(5, 2)), sa.Column("discount_amount", sa.Numeric(10, 2)), sa.Column("minimum_order_amount", sa.Numeric(10, 2), nullable=False, server_default="0"), sa.Column("maximum_discount", sa.Numeric(10, 2)), sa.Column("usage_limit", sa.Integer()), sa.Column("per_user_limit", sa.Integer(), nullable=False, server_default="1"), sa.Column("expires_at", sa.DateTime(timezone=True)), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("code"))
    op.create_index("ix_coupons_code", "coupons", ["code"]); op.create_index("ix_coupons_is_active", "coupons", ["is_active"])
    op.create_table("coupon_usages", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("coupon_id", sa.Integer(), sa.ForeignKey("coupons.id"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("coupon_id", "user_id", "order_id", name="uq_coupon_usage_order"), sa.UniqueConstraint("order_id"))
    op.create_index("ix_coupon_usages_coupon_id", "coupon_usages", ["coupon_id"]); op.create_index("ix_coupon_usages_user_id", "coupon_usages", ["user_id"])

def downgrade():
    op.drop_index("ix_coupon_usages_user_id", table_name="coupon_usages"); op.drop_index("ix_coupon_usages_coupon_id", table_name="coupon_usages"); op.drop_table("coupon_usages"); op.drop_index("ix_coupons_is_active", table_name="coupons"); op.drop_index("ix_coupons_code", table_name="coupons"); op.drop_table("coupons")