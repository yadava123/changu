"""create parcel and ride records

Revision ID: 20260904_20
Revises: 20260904_19
"""
from alembic import op
import sqlalchemy as sa
revision="20260904_20"; down_revision="20260904_19"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("parcels",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("customer_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("driver_id",sa.Integer(),sa.ForeignKey("drivers.id")),sa.Column("pickup_address",sa.Text(),nullable=False),sa.Column("drop_address",sa.Text(),nullable=False),sa.Column("sender_name",sa.String(120),nullable=False),sa.Column("receiver_name",sa.String(120),nullable=False),sa.Column("parcel_type",sa.String(40),nullable=False),sa.Column("weight_kg",sa.Numeric(8,2),nullable=False),sa.Column("price",sa.Numeric(10,2),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_parcels_customer_id","parcels",["customer_id"]);op.create_index("ix_parcels_driver_id","parcels",["driver_id"])
    op.create_table("rides",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("customer_id",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("driver_id",sa.Integer(),sa.ForeignKey("drivers.id")),sa.Column("pickup_address",sa.Text(),nullable=False),sa.Column("destination",sa.Text(),nullable=False),sa.Column("ride_type",sa.String(30),nullable=False),sa.Column("fare",sa.Numeric(10,2),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    op.create_index("ix_rides_customer_id","rides",["customer_id"]);op.create_index("ix_rides_driver_id","rides",["driver_id"])
def downgrade():
    op.drop_index("ix_rides_driver_id",table_name="rides");op.drop_index("ix_rides_customer_id",table_name="rides");op.drop_table("rides");op.drop_index("ix_parcels_driver_id",table_name="parcels");op.drop_index("ix_parcels_customer_id",table_name="parcels");op.drop_table("parcels")