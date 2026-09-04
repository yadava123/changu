"""create vendor application and profile tables

Revision ID: 20260819_07
Revises: 20260819_06
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260819_07"
down_revision = "20260819_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("vendor_applications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("business_name", sa.String(160), nullable=False), sa.Column("business_type", sa.String(40), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("phone", sa.String(15), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("address", sa.String(255), nullable=False), sa.Column("area", sa.String(120), nullable=False), sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False), sa.Column("pincode", sa.String(6), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("admin_notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_vendor_applications_user_id", "vendor_applications", ["user_id"])
    op.create_table("vendors", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False), sa.Column("business_name", sa.String(160), nullable=False), sa.Column("business_type", sa.String(40), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("phone", sa.String(15), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("address", sa.String(255), nullable=False), sa.Column("area", sa.String(120), nullable=False), sa.Column("city", sa.String(80), nullable=False), sa.Column("state", sa.String(80), nullable=False), sa.Column("pincode", sa.String(6), nullable=False), sa.Column("logo_url", sa.String(500)), sa.Column("cover_image_url", sa.String(500)), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
    op.create_index("ix_vendors_user_id", "vendors", ["user_id"])


def downgrade() -> None:
    op.drop_table("vendors")
    op.drop_table("vendor_applications")
