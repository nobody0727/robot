from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WhitelistUserBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    user_name: Optional[str] = Field(None, max_length=255)
    remark: Optional[str] = None
    expire_at: Optional[datetime] = None


class WhitelistUserCreate(WhitelistUserBase):
    pass


class WhitelistUserUpdate(BaseModel):
    user_name: Optional[str] = None
    remark: Optional[str] = None
    expire_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class WhitelistUserResponse(WhitelistUserBase):
    id: int
    added_by: Optional[int]
    added_at: datetime
    is_active: bool
    added_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class WhitelistUserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[WhitelistUserResponse]


class WhitelistCheckRequest(BaseModel):
    user_id: str


class WhitelistCheckResponse(BaseModel):
    user_id: str
    is_whitelisted: bool


class WhitelistStatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
    added_today: int
    expire_soon: int


class WhitelistImportRequest(BaseModel):
    users: list[WhitelistUserCreate]
    override_existing: bool = False


class WhitelistExportResponse(BaseModel):
    total: int
    items: list[WhitelistUserResponse]
