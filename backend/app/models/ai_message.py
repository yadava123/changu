from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class AIMessageRole(str,Enum): USER="USER"; ASSISTANT="ASSISTANT"; SYSTEM="SYSTEM"
class AIMessage(Base):
    __tablename__="ai_messages"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); conversation_id:Mapped[int]=mapped_column(ForeignKey("ai_conversations.id"),nullable=False,index=True); role:Mapped[AIMessageRole]=mapped_column(SqlEnum(AIMessageRole,name="ai_message_role",native_enum=False),nullable=False); content:Mapped[str]=mapped_column(Text,nullable=False); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
