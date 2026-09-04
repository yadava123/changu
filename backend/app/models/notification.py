from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Notification(Base):
    __tablename__="notifications"
    id: Mapped[int]=mapped_column(Integer,primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False,index=True); title: Mapped[str]=mapped_column(String(160),nullable=False); message: Mapped[str]=mapped_column(Text,nullable=False); type: Mapped[str]=mapped_column(String(40),nullable=False); entity_type: Mapped[str|None]=mapped_column(String(30)); entity_id: Mapped[int|None]=mapped_column(Integer); event_key: Mapped[str|None]=mapped_column(String(120),unique=True,index=True); is_read: Mapped[bool]=mapped_column(Boolean,default=False,nullable=False,index=True); read_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,index=True)