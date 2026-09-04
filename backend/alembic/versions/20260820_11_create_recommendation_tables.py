"""create recommendation tables

Revision ID: 20260820_11
Revises: 20260820_10
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
revision="20260820_11"; down_revision="20260820_10"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("user_events",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("event_type",sa.String(40),nullable=False),sa.Column("entity_type",sa.String(30)),sa.Column("entity_id",sa.Integer()),sa.Column("metadata",sa.JSON()),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_user_events_user_id","user_events",["user_id"])
    op.create_table("user_preferences",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),unique=True,nullable=False),sa.Column("preferred_categories",sa.JSON()),sa.Column("preferred_food_types",sa.JSON()),sa.Column("preferred_product_categories",sa.JSON()),sa.Column("preferred_restaurants",sa.JSON()),sa.Column("preferred_price_range",sa.String(20)),sa.Column("personalization_enabled",sa.Boolean(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_table("favorites",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("entity_type",sa.String(30),nullable=False),sa.Column("entity_id",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_index("ix_favorites_user_id","favorites",["user_id"])
    op.create_table("recommendation_events",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("event_type",sa.String(40),nullable=False),sa.Column("entity_type",sa.String(30),nullable=False),sa.Column("entity_id",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)); op.create_table("recommendation_feedback",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("entity_type",sa.String(30),nullable=False),sa.Column("entity_id",sa.Integer(),nullable=False),sa.Column("feedback",sa.String(20),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
def downgrade():
    op.drop_table("recommendation_feedback");op.drop_table("recommendation_events");op.drop_table("favorites");op.drop_table("user_preferences");op.drop_table("user_events")
