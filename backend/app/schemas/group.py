from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time


class BotGroupBase(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=100)
    room_name: Optional[str] = Field(None, max_length=255)
    owner_id: Optional[str] = Field(None, max_length=100)
    owner_name: Optional[str] = Field(None, max_length=255)


class BotGroupCreate(BotGroupBase):
    welcome_enabled: bool = True
    welcome_message: str = "欢迎 {name} 加入群聊！"
    ai_enabled: bool = True
    ai_sleep_start: time = "23:00"
    ai_sleep_end: time = "07:00"


class BotGroupUpdate(BaseModel):
    room_name: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    is_active: Optional[bool] = None
    welcome_enabled: Optional[bool] = None
    welcome_message: Optional[str] = None
    ai_enabled: Optional[bool] = None
    ai_sleep_start: Optional[time] = None
    ai_sleep_end: Optional[time] = None


class WelcomeConfigUpdate(BaseModel):
    welcome_enabled: bool
    welcome_message: str


class AIConfigUpdate(BaseModel):
    ai_enabled: bool
    ai_sleep_start: Optional[time] = None
    ai_sleep_end: Optional[time] = None


class BotGroupResponse(BotGroupBase):
    id: int
    invited_by: Optional[int]
    created_at: datetime
    is_active: bool
    welcome_enabled: bool
    welcome_message: str
    ai_enabled: bool
    ai_sleep_start: time
    ai_sleep_end: time
    last_active: Optional[datetime]
    message_count: Optional[int] = None

    class Config:
        from_attributes = True


class BotGroupListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[BotGroupResponse]


class BotGroupSimple(BaseModel):
    id: int
    room_id: str
    room_name: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
