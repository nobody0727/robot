from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    LoginRequest, LoginResponse, RefreshTokenRequest, 
    TokenResponse, UserResponse
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.core.exceptions import InvalidCredentialsError, AuthenticationError
from app.models.user import AdminUser

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user = auth_service.authenticate_user(request.username, request.password)
        tokens = auth_service.create_tokens(user)
        return LoginResponse(**tokens)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        result = auth_service.refresh_access_token(request.refresh_token)
        return TokenResponse(**result)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout(current_user: AdminUser = Depends(get_current_user)):
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
