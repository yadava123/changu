"""create driver and delivery tables

Revision ID: 20260820_08
Revises: 20260819_07
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa

revision = "20260820_08"
down_revision = "20260819_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("driver_applications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("phone", sa.String(15), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("vehicle_type", sa.String(20), nullable=False), sa.Column("vehicle_number", sa.String(30), nullable=False), sa.Column("license_number", sa.String(40), nullable=False), sa.Column("address", sa.String(255), nullable=False), sa.Column("area", sa.String(120), nullable=False), sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False), sa.Column("pincode", sa.String(6), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("admin_notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_driver_applications_user_id", "driver_applications", ["user_id"])
    op.create_table("drivers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("phone", sa.String(15), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("vehicle_type", sa.String(20), nullable=False), sa.Column("vehicle_number", sa.String(30), nullable=False), sa.Column("license_number", sa.String(40), nullable=False), sa.Column("address", sa.String(255), nullable=False), sa.Column("area", sa.String(120), nullable=False), sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False), sa.Column("pincode", sa.String(6), nullable=False), sa.Column("profile_image_url", sa.String(500)), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("is_online", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_drivers_user_id", "drivers", ["user_id"])
    op.create_table("deliveries", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), unique=True, nullable=False), sa.Column("driver_id", sa.Integer(), sa.ForeignKey("drivers.id")), sa.Column("status", sa.String(30), nullable=False), sa.Column("pickup_address", sa.Text(), nullable=False), sa.Column("delivery_address", sa.Text(), nullable=False), sa.Column("delivery_earning", sa.Integer(), nullable=False), sa.Column("accepted_at", sa.DateTime(timezone=True)), sa.Column("picked_up_at", sa.DateTime(timezone=True)), sa.Column("out_for_delivery_at", sa.DateTime(timezone=True)), sa.Column("delivered_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_deliveries_order_id", "deliveries", ["order_id"])
    op.create_index("ix_deliveries_driver_id", "deliveries", ["driver_id"])


def downgrade() -> None:
    op.drop_table("deliveries")
    op.drop_table("drivers")
    op.drop_table("driver_applications")
