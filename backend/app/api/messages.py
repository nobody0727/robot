from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.schemas.message import (
    GroupMessageCreate, GroupMessageResponse, MessageListResponse, MessageStatsResponse
)
from app.models.message import GroupMessage
from app.models.group import BotGroup
from app.core.dependencies import get_current_user, require_operator
from app.models.user import AdminUser

router = APIRouter(prefix="/messages", tags=["消息管理"])


@router.get("", response_model=MessageListResponse)
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    group_id: Optional[int] = None,
    sender_id: Optional[str] = None,
    keyword: Optional[str] = None,
    msg_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    query = db.query(GroupMessage)
    
    if group_id:
        query = query.filter(GroupMessage.group_id == group_id)
    
    if sender_id:
        query = query.filter(GroupMessage.sender_id == sender_id)
    
    if keyword:
        query = query.filter(GroupMessage.content.ilike(f"%{keyword}%"))
    
    if msg_type:
        query = query.filter(GroupMessage.msg_type == msg_type)
    
    if start_date:
        query = query.filter(GroupMessage.created_at >= start_date)
    
    if end_date:
        query = query.filter(GroupMessage.created_at <= end_date)
    
    total = query.count()
    
    messages = query.order_by(GroupMessage.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    items = []
    for msg in messages:
        msg_dict = GroupMessageResponse.model_validate(msg)
        if msg.group:
            msg_dict.group_name = msg.group.room_name
        items.append(msg_dict)
    
    return MessageListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{message_id}", response_model=GroupMessageResponse)
async def get_message(
    message_id: int,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    message = db.query(GroupMessage).filter(GroupMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    
    msg_dict = GroupMessageResponse.model_validate(message)
    if message.group:
        msg_dict.group_name = message.group.room_name
    return msg_dict


@router.get("/stats/overview", response_model=MessageStatsResponse)
async def get_message_stats(
    group_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=30),
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    query = db.query(GroupMessage).filter(GroupMessage.created_at >= start_date)
    
    if group_id:
        query = query.filter(GroupMessage.group_id == group_id)
    
    total_messages = query.count()
    total_text_messages = query.filter(GroupMessage.msg_type == "text").count()
    total_recalls = query.filter(GroupMessage.is_recalled == True).count()
    
    unique_senders = db.query(func.count(func.distinct(GroupMessage.sender_id))).filter(
        GroupMessage.created_at >= start_date
    )
    if group_id:
        unique_senders = unique_senders.filter(GroupMessage.group_id == group_id)
    unique_senders = unique_senders.scalar()
    
    messages_by_day_query = db.query(
        func.date(GroupMessage.created_at).label("date"),
        func.count(GroupMessage.id).label("count")
    ).filter(GroupMessage.created_at >= start_date)
    
    if group_id:
        messages_by_day_query = messages_by_day_query.filter(GroupMessage.group_id == group_id)
    
    messages_by_day = messages_by_day_query.group_by(func.date(GroupMessage.created_at)).order_by(func.date(GroupMessage.created_at)).all()
    messages_by_day = [{"date": str(m.date), "count": m.count} for m in messages_by_day]
    
    top_senders_query = db.query(
        GroupMessage.sender_id,
        GroupMessage.sender_name,
        func.count(GroupMessage.id).label("count")
    ).filter(GroupMessage.created_at >= start_date)
    
    if group_id:
        top_senders_query = top_senders_query.filter(GroupMessage.group_id == group_id)
    
    top_senders = top_senders_query.group_by(GroupMessage.sender_id, GroupMessage.sender_name) \
        .order_by(func.count(GroupMessage.id).desc()) \
        .limit(10) \
        .all()
    top_senders = [{"sender_id": s.sender_id, "sender_name": s.sender_name, "count": s.count} for s in top_senders]
    
    return MessageStatsResponse(
        total_messages=total_messages,
        total_text_messages=total_text_messages,
        total_recalls=total_recalls,
        unique_senders=unique_senders,
        messages_by_day=messages_by_day,
        top_senders=top_senders
    )
