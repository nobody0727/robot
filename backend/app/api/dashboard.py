from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.message import GroupMessage
from app.models.group import BotGroup
from app.models.whitelist import WhitelistUser
from app.core.dependencies import get_current_user, require_operator
from app.models.user import AdminUser

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/overview")
async def get_overview(
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    total_groups = db.query(func.count(BotGroup.id)).filter(BotGroup.is_active == True).scalar()
    
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_messages_7d = db.query(func.count(GroupMessage.id)).filter(
        GroupMessage.created_at >= seven_days_ago
    ).scalar()
    
    total_whitelist = db.query(func.count(WhitelistUser.id)).filter(WhitelistUser.is_active == True).scalar()
    
    active_users_7d = db.query(func.count(func.distinct(GroupMessage.sender_id))).filter(
        GroupMessage.created_at >= seven_days_ago
    ).scalar()
    
    message_trend_query = db.query(
        func.date(GroupMessage.created_at).label("date"),
        func.count(GroupMessage.id).label("count")
    ).filter(GroupMessage.created_at >= seven_days_ago).group_by(
        func.date(GroupMessage.created_at)
    ).order_by(func.date(GroupMessage.created_at)).all()
    
    message_trend = [{"date": str(m.date), "count": m.count} for m in message_trend_query]
    
    top_groups_query = db.query(
        BotGroup.id,
        BotGroup.room_name,
        func.count(GroupMessage.id).label("message_count")
    ).join(GroupMessage).filter(
        GroupMessage.created_at >= seven_days_ago
    ).group_by(BotGroup.id, BotGroup.room_name).order_by(
        func.count(GroupMessage.id).desc()
    ).limit(5).all()
    
    top_groups = [{"id": g.id, "name": g.room_name or "未知群聊", "message_count": g.message_count} for g in top_groups_query]
    
    return {
        "total_groups": total_groups,
        "total_messages_7d": total_messages_7d,
        "total_whitelist_users": total_whitelist,
        "active_users_7d": active_users_7d,
        "message_trend": message_trend,
        "top_groups": top_groups
    }


@router.get("/group/{group_id}")
async def get_group_stats(
    group_id: int,
    days: int = Query(7, ge=1, le=30),
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    group = db.query(BotGroup).filter(BotGroup.id == group_id).first()
    if not group:
        return {"error": "群组不存在"}
    
    total_messages = db.query(func.count(GroupMessage.id)).filter(
        GroupMessage.group_id == group_id,
        GroupMessage.created_at >= start_date
    ).scalar()
    
    unique_senders = db.query(func.count(func.distinct(GroupMessage.sender_id))).filter(
        GroupMessage.group_id == group_id,
        GroupMessage.created_at >= start_date
    ).scalar()
    
    message_trend_query = db.query(
        func.date(GroupMessage.created_at).label("date"),
        func.count(GroupMessage.id).label("count")
    ).filter(
        GroupMessage.group_id == group_id,
        GroupMessage.created_at >= start_date
    ).group_by(func.date(GroupMessage.created_at)).order_by(func.date(GroupMessage.created_at)).all()
    
    message_trend = [{"date": str(m.date), "count": m.count} for m in message_trend_query]
    
    top_senders_query = db.query(
        GroupMessage.sender_id,
        GroupMessage.sender_name,
        func.count(GroupMessage.id).label("count")
    ).filter(
        GroupMessage.group_id == group_id,
        GroupMessage.created_at >= start_date
    ).group_by(GroupMessage.sender_id, GroupMessage.sender_name).order_by(
        func.count(GroupMessage.id).desc()
    ).limit(10).all()
    
    top_senders = [{"sender_id": s.sender_id, "sender_name": s.sender_name or "未知用户", "count": s.count} for s in top_senders_query]
    
    return {
        "group_id": group_id,
        "group_name": group.room_name,
        "total_messages": total_messages,
        "unique_senders": unique_senders,
        "message_trend": message_trend,
        "top_senders": top_senders
    }


@router.get("/activity")
async def get_activity_trend(
    days: int = Query(30, ge=1, le=90),
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    activity_query = db.query(
        func.date(GroupMessage.created_at).label("date"),
        func.count(GroupMessage.id).label("message_count"),
        func.count(func.distinct(GroupMessage.sender_id)).label("user_count"),
        func.count(func.distinct(GroupMessage.group_id)).label("group_count")
    ).filter(GroupMessage.created_at >= start_date).group_by(
        func.date(GroupMessage.created_at)
    ).order_by(func.date(GroupMessage.created_at)).all()
    
    activity = [
        {
            "date": str(a.date),
            "message_count": a.message_count,
            "user_count": a.user_count,
            "group_count": a.group_count
        }
        for a in activity_query
    ]
    
    return {"activity": activity, "days": days}


@router.get("/whitelist")
async def get_whitelist_stats(
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    total = db.query(func.count(WhitelistUser.id)).scalar()
    active = db.query(func.count(WhitelistUser.id)).filter(WhitelistUser.is_active == True).scalar()
    
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    added_today = db.query(func.count(WhitelistUser.id)).filter(
        WhitelistUser.added_at >= today_start
    ).scalar()
    
    this_month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    added_this_month = db.query(func.count(WhitelistUser.id)).filter(
        WhitelistUser.added_at >= this_month_start
    ).scalar()
    
    soon = datetime.now(timezone.utc) + timedelta(hours=24)
    expire_soon = db.query(func.count(WhitelistUser.id)).filter(
        WhitelistUser.is_active == True,
        WhitelistUser.expire_at.isnot(None),
        WhitelistUser.expire_at <= soon,
        WhitelistUser.expire_at > datetime.now(timezone.utc)
    ).scalar()
    
    expired = db.query(func.count(WhitelistUser.id)).filter(
        WhitelistUser.expire_at.isnot(None),
        WhitelistUser.expire_at <= datetime.now(timezone.utc)
    ).scalar()
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "added_today": added_today,
        "added_this_month": added_this_month,
        "expire_soon": expire_soon,
        "expired": expired
    }
