"""add parcel payment status

Revision ID: 20260904_24
Revises: 20260904_23
"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_24"
down_revision = "20260904_23"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("parcels") as batch:
        batch.add_column(sa.Column("payment_status", sa.String(length=8), nullable=False, server_default="PENDING"))


def downgrade():
    with op.batch_alter_table("parcels") as batch:
        batch.drop_column("payment_status")