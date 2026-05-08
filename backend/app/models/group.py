from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class BotGroup(Base):
    __tablename__ = "bot_groups"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(100), unique=True, nullable=False, index=True)
    room_name = Column(String(255), nullable=True)
    owner_id = Column(String(100), nullable=True)
    owner_name = Column(String(255), nullable=True)
    invited_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, default="欢迎 {name} 加入群聊！")
    ai_enabled = Column(Boolean, default=True)
    ai_sleep_start = Column(Time, default="23:00")
    ai_sleep_end = Column(Time, default="07:00")
    last_active = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")
    invited_by_user = relationship("AdminUser", back_populates="bot_groups")
