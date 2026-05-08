from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.models.whitelist import WhitelistUser
from app.models.user import AdminUser
from app.schemas.whitelist import WhitelistUserCreate, WhitelistUserUpdate
from app.core.exceptions import WhitelistUserNotFoundError, WhitelistUserExistsError, WhitelistImportError
import redis.asyncio as redis


class WhitelistService:
    def __init__(self, db: Session, redis_conn: Optional[redis.Redis] = None):
        self.db = db
        self.redis = redis_conn

    def get_user_by_id(self, user_id: int) -> WhitelistUser:
        user = self.db.query(WhitelistUser).filter(WhitelistUser.id == user_id).first()
        if not user:
            raise WhitelistUserNotFoundError()
        return user

    def get_user_by_wxid(self, wxid: str) -> Optional[WhitelistUser]:
        return self.db.query(WhitelistUser).filter(
            WhitelistUser.user_id == wxid,
            WhitelistUser.is_active == True
        ).first()

    async def check_whitelist(self, wxid: str) -> bool:
        if self.redis:
            cached = await self.redis.get(f"whitelist:{wxid}")
            if cached is not None:
                return cached == "1"
        
        user = self.get_user_by_wxid(wxid)
        is_whitelisted = user is not None and (user.expire_at is None or user.expire_at > datetime.now(timezone.utc))
        
        if self.redis:
            await self.redis.setex(f"whitelist:{wxid}", 300, "1" if is_whitelisted else "0")
        
        return is_whitelisted

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        expire_soon: bool = False
    ) -> dict:
        query = self.db.query(WhitelistUser)
        
        if keyword:
            query = query.filter(
                or_(
                    WhitelistUser.user_id.ilike(f"%{keyword}%"),
                    WhitelistUser.user_name.ilike(f"%{keyword}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(WhitelistUser.is_active == is_active)
        
        if expire_soon:
            soon = datetime.now(timezone.utc) + timedelta(hours=24)
            query = query.filter(
                and_(
                    WhitelistUser.expire_at.isnot(None),
                    WhitelistUser.expire_at <= soon,
                    WhitelistUser.expire_at > datetime.now(timezone.utc)
                )
            )
        
        total = query.count()
        
        users = query.order_by(WhitelistUser.added_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        items = []
        for user in users:
            user_dict = {
                "id": user.id,
                "user_id": user.user_id,
                "user_name": user.user_name,
                "added_by": user.added_by,
                "added_at": user.added_at,
                "expire_at": user.expire_at,
                "remark": user.remark,
                "is_active": user.is_active,
                "added_by_name": user.added_by_user.username if user.added_by_user else None
            }
            items.append(user_dict)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    def create_user(self, user_data: WhitelistUserCreate, added_by: int) -> WhitelistUser:
        existing = self.get_user_by_wxid(user_data.user_id)
        if existing:
            raise WhitelistUserExistsError()
        
        user = WhitelistUser(
            user_id=user_data.user_id,
            user_name=user_data.user_name,
            added_by=added_by,
            expire_at=user_data.expire_at,
            remark=user_data.remark,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        if self.redis:
            import asyncio
            asyncio.create_task(self.redis.delete(f"whitelist:{user_data.user_id}"))
        
        return user

    def update_user(self, user_id: int, user_data: WhitelistUserUpdate) -> WhitelistUser:
        user = self.get_user_by_id(user_id)
        
        if user_data.user_name is not None:
            user.user_name = user_data.user_name
        
        if user_data.remark is not None:
            user.remark = user_data.remark
        
        if user_data.expire_at is not None:
            user.expire_at = user_data.expire_at
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
            if self.redis:
                import asyncio
                asyncio.create_task(self.redis.delete(f"whitelist:{user.user_id}"))
        
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
        
        if self.redis:
            import asyncio
            asyncio.create_task(self.redis.delete(f"whitelist:{user.user_id}"))
        
        return True

    def import_users(self, users_data: List[WhitelistUserCreate], added_by: int, override_existing: bool = False) -> dict:
        imported = 0
        skipped = 0
        errors = []
        
        for idx, user_data in enumerate(users_data):
            try:
                existing = self.get_user_by_wxid(user_data.user_id)
                
                if existing:
                    if override_existing:
                        existing.user_name = user_data.user_name or existing.user_name
                        existing.remark = user_data.remark or existing.remark
                        existing.added_by = added_by
                        existing.is_active = True
                        imported += 1
                    else:
                        skipped += 1
                        continue
                else:
                    user = WhitelistUser(
                        user_id=user_data.user_id,
                        user_name=user_data.user_name,
                        added_by=added_by,
                        expire_at=user_data.expire_at,
                        remark=user_data.remark,
                        is_active=True
                    )
                    self.db.add(user)
                    imported += 1
                
            except Exception as e:
                errors.append({"index": idx, "user_id": user_data.user_id, "error": str(e)})
        
        self.db.commit()
        
        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }

    def get_stats(self) -> dict:
        total = self.db.query(WhitelistUser).count()
        active = self.db.query(WhitelistUser).filter(WhitelistUser.is_active == True).count()
        inactive = total - active
        
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        added_today = self.db.query(WhitelistUser).filter(WhitelistUser.added_at >= today_start).count()
        
        soon = datetime.now(timezone.utc) + timedelta(hours=24)
        expire_soon = self.db.query(WhitelistUser).filter(
            and_(
                WhitelistUser.is_active == True,
                WhitelistUser.expire_at.isnot(None),
                WhitelistUser.expire_at <= soon,
                WhitelistUser.expire_at > datetime.now(timezone.utc)
            )
        ).count()
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "added_today": added_today,
            "expire_soon": expire_soon
        }
