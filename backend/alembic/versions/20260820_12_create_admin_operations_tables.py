"""create admin operations tables

Revision ID: 20260820_12
Revises: 20260820_11
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
revision="20260820_12"; down_revision="20260820_11"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("audit_logs",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("admin_user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("action",sa.String(80),nullable=False),sa.Column("entity_type",sa.String(40),nullable=False),sa.Column("entity_id",sa.Integer()),sa.Column("old_value",sa.Text()),sa.Column("new_value",sa.Text()),sa.Column("reason",sa.Text()),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_audit_logs_action","audit_logs",["action"]); op.create_index("ix_audit_logs_created_at","audit_logs",["created_at"])
    op.create_table("platform_settings",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("key",sa.String(80),unique=True,nullable=False),sa.Column("value",sa.String(255),nullable=False),sa.Column("description",sa.Text()),sa.Column("updated_by",sa.Integer(),sa.ForeignKey("users.id")),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_platform_settings_key","platform_settings",["key"])
def downgrade(): op.drop_table("platform_settings");op.drop_table("audit_logs")
