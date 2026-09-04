"""create AI tables

Revision ID: 20260820_10
Revises: 20260820_09
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
revision="20260820_10"; down_revision="20260820_09"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("ai_conversations",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("title",sa.String(160),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_ai_conversations_user_id","ai_conversations",["user_id"])
    op.create_table("ai_messages",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("conversation_id",sa.Integer(),sa.ForeignKey("ai_conversations.id"),nullable=False),sa.Column("role",sa.String(20),nullable=False),sa.Column("content",sa.Text(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_ai_messages_conversation_id","ai_messages",["conversation_id"])
    op.create_table("ai_usage",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("conversation_id",sa.Integer(),sa.ForeignKey("ai_conversations.id")),sa.Column("provider",sa.String(40),nullable=False),sa.Column("request_count",sa.Integer(),nullable=False),sa.Column("estimated_tokens",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_ai_usage_user_id","ai_usage",["user_id"])
def downgrade():
    op.drop_table("ai_usage"); op.drop_table("ai_messages"); op.drop_table("ai_conversations")
