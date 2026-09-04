"""add AI preference controls

Revision ID: 20260905_26
Revises: 20260904_25
"""
from alembic import op
import sqlalchemy as sa

revision = "20260905_26"
down_revision = "20260904_25"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user_preferences") as batch:
        batch.add_column(sa.Column("memory_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.add_column(sa.Column("recommendations_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table("user_preferences") as batch:
        batch.drop_column("recommendations_enabled")
        batch.drop_column("memory_enabled")