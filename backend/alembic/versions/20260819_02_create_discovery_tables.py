"""create discovery tables

Revision ID: 20260819_02
Revises: 20260819_01
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260819_02"
down_revision = "20260819_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_restaurants_name", "restaurants", ["name"])
    op.create_index("ix_restaurants_owner_id", "restaurants", ["owner_id"])
    op.create_index("ix_restaurants_city", "restaurants", ["city"])
    op.create_index("ix_restaurants_is_active", "restaurants", ["is_active"])

    op.create_table(
        "food_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_food_items_restaurant_id", "food_items", ["restaurant_id"])
    op.create_index("ix_food_items_name", "food_items", ["name"])
    op.create_index("ix_food_items_category", "food_items", ["category"])
    op.create_index("ix_food_items_is_available", "food_items", ["is_available"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_seller_id", "products", ["seller_id"])
    op.create_index("ix_products_is_available", "products", ["is_available"])


def downgrade() -> None:
    op.drop_table("products")
    op.drop_table("food_items")
    op.drop_table("restaurants")
