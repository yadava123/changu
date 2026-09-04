"""create commerce tables

Revision ID: 20260819_03
Revises: 20260819_02
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260819_03"
down_revision = "20260819_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("addresses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("phone", sa.String(15), nullable=False), sa.Column("address_line", sa.String(255), nullable=False), sa.Column("area", sa.String(120), nullable=False), sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False), sa.Column("pincode", sa.String(6), nullable=False), sa.Column("latitude", sa.Float()), sa.Column("longitude", sa.Float()), sa.Column("is_default", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_addresses_user_id", "addresses", ["user_id"])
    op.create_table("carts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_carts_user_id", "carts", ["user_id"])
    op.create_table("cart_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id"), nullable=False), sa.Column("food_item_id", sa.Integer(), sa.ForeignKey("food_items.id")), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("unit_price", sa.Numeric(10, 2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_cart_items_cart_id", "cart_items", ["cart_id"])
    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_number", sa.String(20), unique=True, nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id")), sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("status", sa.String(30), nullable=False), sa.Column("subtotal", sa.Numeric(10, 2), nullable=False), sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=False), sa.Column("tax", sa.Numeric(10, 2), nullable=False), sa.Column("discount", sa.Numeric(10, 2), nullable=False), sa.Column("total_amount", sa.Numeric(10, 2), nullable=False), sa.Column("payment_method", sa.String(30), nullable=False), sa.Column("payment_status", sa.String(20), nullable=False), sa.Column("delivery_address", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_orders_order_number", "orders", ["order_number"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_table("order_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("food_item_id", sa.Integer(), sa.ForeignKey("food_items.id")), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")), sa.Column("item_name", sa.String(160), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("unit_price", sa.Numeric(10, 2), nullable=False), sa.Column("total_price", sa.Numeric(10, 2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("addresses")
