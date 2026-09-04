"""create order reviews

Revision ID: 20260904_16
Revises: 20260904_15
"""
from alembic import op
import sqlalchemy as sa
revision = "20260904_16"
down_revision = "20260904_15"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("reviews", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("rating", sa.Integer(), nullable=False), sa.Column("comment", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating"), sa.UniqueConstraint("user_id", "order_id", name="uq_reviews_user_order"))
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])
    op.create_index("ix_reviews_order_id", "reviews", ["order_id"])

def downgrade():
    op.drop_index("ix_reviews_order_id", table_name="reviews"); op.drop_index("ix_reviews_user_id", table_name="reviews"); op.drop_table("reviews")