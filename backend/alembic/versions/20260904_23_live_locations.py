"""add current driver and provider locations

Revision ID: 20260904_23
Revises: 20260904_22
"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_23"
down_revision = "20260904_22"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("drivers") as batch:
        batch.add_column(sa.Column("latitude", sa.Float(), nullable=True))
        batch.add_column(sa.Column("longitude", sa.Float(), nullable=True))
    with op.batch_alter_table("emergency_providers") as batch:
        batch.add_column(sa.Column("latitude", sa.Float(), nullable=True))
        batch.add_column(sa.Column("longitude", sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table("emergency_providers") as batch:
        batch.drop_column("longitude")
        batch.drop_column("latitude")
    with op.batch_alter_table("drivers") as batch:
        batch.drop_column("longitude")
        batch.drop_column("latitude")