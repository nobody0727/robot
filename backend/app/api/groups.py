from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.group import (
    BotGroupCreate, BotGroupUpdate, BotGroupResponse, BotGroupListResponse,
    WelcomeConfigUpdate, AIConfigUpdate
)
from app.models.group import BotGroup
from app.models.message import GroupMessage
from app.core.dependencies import get_current_user, require_admin, require_super_admin, require_operator
from app.core.exceptions import GroupNotFoundError, GroupAlreadyExistsError
from app.models.user import AdminUser

router = APIRouter(prefix="/groups", tags=["群组管理"])


@router.get("", response_model=BotGroupListResponse)
async def list_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    query = db.query(BotGroup)
    
    if keyword:
        query = query.filter(BotGroup.room_name.ilike(f"%{keyword}%") | BotGroup.room_id.ilike(f"%{keyword}%"))
    
    if is_active is not None:
        query = query.filter(BotGroup.is_active == is_active)
    
    total = query.count()
    
    groups = query.order_by(BotGroup.last_active.desc().nullslast(), BotGroup.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    items = []
    for group in groups:
        message_count = db.query(func.count(GroupMessage.id)).filter(GroupMessage.group_id == group.id).scalar()
        group_dict = BotGroupResponse.model_validate(group)
        group_dict.message_count = message_count
        items.append(group_dict)
    
    return BotGroupListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{group_id}", response_model=BotGroupResponse)
async def get_group(
    group_id: int,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="群组不存在")
    
    message_count = db.query(func.count(GroupMessage.id)).filter(GroupMessage.group_id == group.id).scalar()
    group_dict = BotGroupResponse.model_validate(group)
    group_dict.message_count = message_count
    return group_dict


@router.post("", response_model=BotGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: BotGroupCreate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(BotGroup).filter(BotGroup.room_id == group_data.room_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="群组已存在")
    
    group = BotGroup(
        room_id=group_data.room_id,
        room_name=group_data.room_name,
        owner_id=group_data.owner_id,
        owner_name=group_data.owner_name,
        invited_by=current_user.id,
        welcome_enabled=group_data.welcome_enabled,
        welcome_message=group_data.welcome_message,
        ai_enabled=group_data.ai_enabled,
        ai_sleep_start=group_data.ai_sleep_start,
        ai_sleep_end=group_data.ai_sleep_end
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return BotGroupResponse.model_validate(group)


@router.put("/{group_id}", response_model=BotGroupResponse)
async def update_group(
    group_id: int,
    group_data: BotGroupUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="群组不存在")
    
    update_data = group_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)
    
    db.commit()
    db.refresh(group)
    
    message_count = db.query(func.count(GroupMessage.id)).filter(GroupMessage.group_id == group.id).scalar()
    group_dict = BotGroupResponse.model_validate(group)
    group_dict.message_count = message_count
    return group_dict


@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="群组不存在")
    
    db.delete(group)
    db.commit()
    
    return {"message": "群组删除成功"}


@router.put("/{group_id}/welcome", response_model=BotGroupResponse)
async def update_welcome_config(
    group_id: int,
    welcome_data: WelcomeConfigUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="群组不存在")
    
    group.welcome_enabled = welcome_data.welcome_enabled
    group.welcome_message = welcome_data.welcome_message
    
    db.commit()
    db.refresh(group)
    
    return BotGroupResponse.model_validate(group)


@router.put("/{group_id}/ai", response_model=BotGroupResponse)
async def update_ai_config(
    group_id: int,
    ai_data: AIConfigUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="群组不存在")
    
    group.ai_enabled = ai_data.ai_enabled
    if ai_data.ai_sleep_start is not None:
        group.ai_sleep_start = ai_data.ai_sleep_start
    if ai_data.ai_sleep_end is not None:
        group.ai_sleep_end = ai_data.ai_sleep_end
    
    db.commit()
    db.refresh(group)
    
    return BotGroupResponse.model_validate(group)
