from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.security import verify_access_token
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.models.user import AdminUser

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    token = credentials.credentials
    
    user_id = verify_access_token(token)
    if not user_id:
        raise AuthenticationError("无效或过期的Token")
    
    user = db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    if not user.is_active:
        raise AuthenticationError("用户已被禁用")
    
    return user


def require_role(*roles):
    async def role_checker(current_user: AdminUser = Depends(get_current_user)) -> AdminUser:
        if current_user.role not in roles:
            raise PermissionDeniedError("您没有权限执行此操作")
        return current_user
    return role_checker


def require_admin():
    return require_role("admin", "super_admin")


def require_super_admin():
    return require_role("super_admin")


def require_operator():
    return require_role("operator", "admin", "super_admin")


class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))
        self.skip = (self.page - 1) * self.page_size


def get_pagination_params(page: int = 1, page_size: int = 20) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
