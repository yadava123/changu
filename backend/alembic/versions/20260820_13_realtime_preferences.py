"""add notification preferences

Revision ID: 20260820_13
Revises: 20260820_12
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
revision="20260820_13"; down_revision="20260820_12"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("notification_preferences",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),unique=True,nullable=False),sa.Column("order_updates",sa.Boolean(),nullable=False),sa.Column("delivery_updates",sa.Boolean(),nullable=False),sa.Column("payment_updates",sa.Boolean(),nullable=False),sa.Column("promotions",sa.Boolean(),nullable=False),sa.Column("loyalty",sa.Boolean(),nullable=False),sa.Column("referrals",sa.Boolean(),nullable=False),sa.Column("system_notifications",sa.Boolean(),nullable=False))
def downgrade(): op.drop_table("notification_preferences")
