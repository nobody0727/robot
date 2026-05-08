from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional, Dict, List
from bot.src.config import settings

Base = declarative_base()


class GroupMessage(Base):
    __tablename__ = "group_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("bot_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(100), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    content_vector = Column(Text, nullable=True)
    msg_type = Column(String(50), default="text")
    is_recalled = Column(Boolean, default=False)
    raw_msg_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    extra_data = Column(JSON, nullable=True)


class BotGroup(Base):
    __tablename__ = "bot_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(100), unique=True, nullable=False, index=True)
    room_name = Column(String(255), nullable=True)
    owner_id = Column(String(100), nullable=True)
    owner_name = Column(String(255), nullable=True)
    invited_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, default="欢迎 {name} 加入群聊！")
    ai_enabled = Column(Boolean, default=True)
    ai_sleep_start = Column(String(10), default="23:00")
    ai_sleep_end = Column(String(10), default="07:00")
    last_active = Column(DateTime(timezone=True), nullable=True)


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class MessageStore:
    def __init__(self):
        self.session_factory = async_session
    
    async def create_message(
        self,
        group_id: int,
        sender_id: str,
        content: str,
        msg_type: str = "text",
        sender_name: Optional[str] = None,
        raw_msg_id: Optional[str] = None,
        extra_data: Optional[Dict] = None
    ) -> GroupMessage:
        async with self.session_factory() as session:
            message = GroupMessage(
                group_id=group_id,
                sender_id=sender_id,
                sender_name=sender_name,
                content=content,
                msg_type=msg_type,
                raw_msg_id=raw_msg_id,
                extra_data=extra_data
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
    
    async def mark_message_recalled(self, raw_msg_id: str):
        async with self.session_factory() as session:
            from sqlalchemy import update
            await session.execute(
                update(GroupMessage)
                .where(GroupMessage.raw_msg_id == raw_msg_id)
                .values(is_recalled=True)
            )
            await session.commit()
    
    async def get_group_by_room_id(self, room_id: str) -> Optional[BotGroup]:
        async with self.session_factory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(BotGroup).where(BotGroup.room_id == room_id)
            )
            return result.scalar_one_or_none()
    
    async def create_or_update_group(
        self,
        room_id: str,
        room_name: Optional[str] = None,
        owner_id: Optional[str] = None,
        owner_name: Optional[str] = None
    ) -> BotGroup:
        async with self.session_factory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(BotGroup).where(BotGroup.room_id == room_id)
            )
            group = result.scalar_one_or_none()
            
            if group:
                if room_name:
                    group.room_name = room_name
                if owner_id:
                    group.owner_id = owner_id
                if owner_name:
                    group.owner_name = owner_name
                group.last_active = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(group)
                return group
            else:
                group = BotGroup(
                    room_id=room_id,
                    room_name=room_name,
                    owner_id=owner_id,
                    owner_name=owner_name
                )
                session.add(group)
                await session.commit()
                await session.refresh(group)
                return group
    
    async def update_group_activity(self, room_id: str):
        async with self.session_factory() as session:
            from sqlalchemy import update
            await session.execute(
                update(BotGroup)
                .where(BotGroup.room_id == room_id)
                .values(last_active=datetime.now(timezone.utc))
            )
            await session.commit()
