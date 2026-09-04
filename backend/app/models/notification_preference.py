from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class NotificationPreference(Base):
    __tablename__='notification_preferences'
    id:Mapped[int]=mapped_column(Integer,primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),unique=True,nullable=False)
    order_updates:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); delivery_updates:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); payment_updates:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); promotions:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); loyalty:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); referrals:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); system_notifications:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
