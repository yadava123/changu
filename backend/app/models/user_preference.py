from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    preferred_categories: Mapped[list | None] = mapped_column(JSON, default=list)
    preferred_food_types: Mapped[list | None] = mapped_column(JSON, default=list)
    preferred_product_categories: Mapped[list | None] = mapped_column(JSON, default=list)
    preferred_restaurants: Mapped[list | None] = mapped_column(JSON, default=list)
    preferred_price_range: Mapped[str | None] = mapped_column(String(20), nullable=True)
    personalization_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    memory_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    recommendations_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
