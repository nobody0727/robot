from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.redis_client import get_redis
from app.schemas.whitelist import (
    WhitelistUserCreate, WhitelistUserUpdate, WhitelistUserResponse,
    WhitelistUserListResponse, WhitelistCheckRequest, WhitelistCheckResponse,
    WhitelistStatsResponse, WhitelistImportRequest, WhitelistExportResponse
)
from app.services.whitelist_service import WhitelistService
from app.core.dependencies import get_current_user, require_admin, require_operator
from app.core.exceptions import WhitelistUserNotFoundError, WhitelistUserExistsError
from app.models.user import AdminUser
import redis.asyncio as redis

router = APIRouter(prefix="/whitelist", tags=["白名单管理"])


@router.get("", response_model=WhitelistUserListResponse)
async def list_whitelist_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    expire_soon: bool = False,
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    result = whitelist_service.list_users(
        page=page, page_size=page_size,
        keyword=keyword, is_active=is_active, expire_soon=expire_soon
    )
    return WhitelistUserListResponse(**result)


@router.get("/stats", response_model=WhitelistStatsResponse)
async def get_whitelist_stats(
    current_user: AdminUser = Depends(require_operator),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    stats = whitelist_service.get_stats()
    return WhitelistStatsResponse(**stats)


@router.post("/check", response_model=WhitelistCheckResponse)
async def check_whitelist(
    request: WhitelistCheckRequest,
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    is_whitelisted = await whitelist_service.check_whitelist(request.user_id)
    return WhitelistCheckResponse(user_id=request.user_id, is_whitelisted=is_whitelisted)


@router.post("", response_model=WhitelistUserResponse, status_code=status.HTTP_201_CREATED)
async def create_whitelist_user(
    user_data: WhitelistUserCreate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    try:
        user = whitelist_service.create_user(user_data, added_by=current_user.id)
        return WhitelistUserResponse.model_validate(user)
    except WhitelistUserExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=WhitelistUserResponse)
async def update_whitelist_user(
    user_id: int,
    user_data: WhitelistUserUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    try:
        user = whitelist_service.update_user(user_id, user_data)
        return WhitelistUserResponse.model_validate(user)
    except WhitelistUserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}")
async def delete_whitelist_user(
    user_id: int,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    try:
        whitelist_service.delete_user(user_id)
        return {"message": "白名单用户移除成功"}
    except WhitelistUserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/import")
async def import_whitelist_users(
    request: WhitelistImportRequest,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    result = whitelist_service.import_users(
        users_data=request.users,
        added_by=current_user.id,
        override_existing=request.override_existing
    )
    return {
        "message": f"导入完成: 成功{result['imported']}条, 跳过{result['skipped']}条",
        "imported": result['imported'],
        "skipped": result['skipped'],
        "errors": result['errors']
    }


@router.get("/export", response_model=WhitelistExportResponse)
async def export_whitelist_users(
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    redis_conn = await get_redis()
    whitelist_service = WhitelistService(db, redis_conn)
    result = whitelist_service.list_users(page=1, page_size=10000)
    return WhitelistExportResponse(total=result["total"], items=result["items"])
