from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index, Time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, TIME
from sqlalchemy.sql import func
from app.database import Base


class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("bot_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(100), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    content_vector = Column(Text, nullable=True)
    msg_type = Column(String(50), default="text", index=True)
    is_recalled = Column(Boolean, default=False, index=True)
    raw_msg_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    extra_data = Column(JSONB, nullable=True)

    group = relationship("BotGroup", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_group_time", "group_id", "created_at"),
        Index("idx_messages_vector", postgresql_using="hnsw", postgresql_ops={"content_vector": "vector_cosine_ops"}),
    )
