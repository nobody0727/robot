from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.auth_service import UserService, AuthService
from app.core.dependencies import get_current_user, require_admin, require_super_admin
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError, PermissionDeniedError
from app.models.user import AdminUser

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    result = user_service.list_users(page=page, page_size=page_size)
    return UserListResponse(**result)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = user_service.get_user_by_id(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        return UserResponse.model_validate(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if current_user.role != "super_admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有权限修改其他用户")
    
    user_service = UserService(db)
    try:
        user = user_service.update_user(user_id, user_data)
        return UserResponse.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己")
    
    user_service = UserService(db)
    try:
        user_service.delete_user(user_id)
        return {"message": "用户删除成功"}
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
