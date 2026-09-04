"""add notification metadata fields

Revision ID: 20260820_14
Revises: 20260820_13
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
revision="20260820_14"; down_revision="20260820_13"; branch_labels=None; depends_on=None
def upgrade():
    with op.batch_alter_table("notifications") as b:
        b.add_column(sa.Column("entity_type",sa.String(30)));b.add_column(sa.Column("entity_id",sa.Integer()));b.add_column(sa.Column("event_key",sa.String(120)));b.add_column(sa.Column("read_at",sa.DateTime(timezone=True)));b.alter_column("type",type_=sa.String(40));b.create_index("ix_notifications_event_key",["event_key"],unique=True);b.create_index("ix_notifications_is_read",["is_read"])
def downgrade():
    with op.batch_alter_table("notifications") as b:b.drop_index("ix_notifications_is_read");b.drop_index("ix_notifications_event_key");b.drop_column("read_at");b.drop_column("event_key");b.drop_column("entity_id");b.drop_column("entity_type")
