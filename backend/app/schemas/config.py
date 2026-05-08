from pydantic import BaseModel
from typing import Any, Optional


class ConfigBase(BaseModel):
    key: str
    value: Any


class ConfigUpdate(BaseModel):
    value: Any


class ConfigResponse(ConfigBase):
    description: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class ConfigListResponse(BaseModel):
    items: list[ConfigResponse]


class WhitelistConfig(BaseModel):
    enable_whitelist: bool = True
    welcome_msg: str = "欢迎使用微信机器人！"
    reject_msg: str = "您暂无权限使用此功能，请联系管理员添加白名单。"


class AIConfig(BaseModel):
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000


class BotConfig(BaseModel):
    name: str = "微信助手"
    sleep_enabled: bool = True
    sleep_start: str = "23:00"
    sleep_end: str = "07:00"
