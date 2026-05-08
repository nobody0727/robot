from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WhitelistUser(Base):
    __tablename__ = "whitelist_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    user_name = Column(String(255), nullable=True)
    added_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    expire_at = Column(DateTime(timezone=True), nullable=True)
    remark = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    added_by_user = relationship("AdminUser", back_populates="whitelist_users")
