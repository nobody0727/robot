from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    msg_type: str = "text"


class GroupMessageCreate(MessageBase):
    group_id: int
    sender_id: str
    sender_name: Optional[str] = None
    raw_msg_id: Optional[str] = None
    extra_data: Optional[dict] = None


class GroupMessageResponse(MessageBase):
    id: int
    group_id: int
    sender_id: str
    sender_name: Optional[str]
    is_recalled: bool
    raw_msg_id: Optional[str]
    created_at: datetime
    extra_data: Optional[dict]
    group_name: Optional[str] = None

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[GroupMessageResponse]


class MessageStatsResponse(BaseModel):
    total_messages: int
    total_text_messages: int
    total_recalls: int
    unique_senders: int
    messages_by_day: list[dict]
    top_senders: list[dict]


class RecallUpdate(BaseModel):
    is_recalled: bool = True


class RecallResponse(BaseModel):
    id: int
    raw_msg_id: str
    is_recalled: bool
    recovered_content: Optional[str] = None

    class Config:
        from_attributes = True
