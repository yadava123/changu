from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class AIUsage(Base):
    __tablename__="ai_usage"
    id:Mapped[int]=mapped_column(Integer,primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False,index=True); conversation_id:Mapped[int|None]=mapped_column(ForeignKey("ai_conversations.id")); provider:Mapped[str]=mapped_column(String(40),nullable=False); request_count:Mapped[int]=mapped_column(Integer,default=1,nullable=False); estimated_tokens:Mapped[int]=mapped_column(Integer,default=0,nullable=False); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
