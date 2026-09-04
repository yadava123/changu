"""add throttled realtime presence timestamps

Revision ID: 20260904_15
Revises: 20260820_14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_15"
down_revision = "20260820_14"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("drivers") as batch:
        batch.add_column(sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True))
        batch.create_index("ix_drivers_last_seen", ["last_seen"])
    with op.batch_alter_table("emergency_providers") as batch:
        batch.add_column(sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True))
        batch.create_index("ix_emergency_providers_last_seen", ["last_seen"])


def downgrade():
    with op.batch_alter_table("emergency_providers") as batch:
        batch.drop_index("ix_emergency_providers_last_seen")
        batch.drop_column("last_seen")
    with op.batch_alter_table("drivers") as batch:
        batch.drop_index("ix_drivers_last_seen")
        batch.drop_column("last_seen")