from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
class AIConversation(Base):
    __tablename__="ai_conversations"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False,index=True); title:Mapped[str]=mapped_column(String(160),default="New Chat",nullable=False); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False); messages=relationship("AIMessage",cascade="all, delete-orphan")
