from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.user import AdminUser
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.exceptions import InvalidCredentialsError, UserNotFoundError, UserAlreadyExistsError
from app.schemas.user import UserCreate, UserUpdate


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> AdminUser:
        user = self.db.query(AdminUser).filter(AdminUser.username == username).first()
        
        if not user:
            raise InvalidCredentialsError()
        
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        if not user.is_active:
            raise InvalidCredentialsError("用户已被禁用")
        
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        
        return user

    def create_tokens(self, user: AdminUser) -> dict:
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 7200,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active
            }
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        from app.core.security import verify_refresh_token
        
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise InvalidCredentialsError("无效的Refresh Token")
        
        user = self.db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
        if not user or not user.is_active:
            raise InvalidCredentialsError("用户不存在或已被禁用")
        
        new_access_token = create_access_token(str(user.id))
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 7200
        }


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> AdminUser:
        user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user

    def get_user_by_username(self, username: str) -> AdminUser:
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()

    def list_users(self, page: int = 1, page_size: int = 20) -> dict:
        query = self.db.query(AdminUser)
        total = query.count()
        
        users = query.order_by(AdminUser.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": users
        }

    def create_user(self, user_data: UserCreate) -> AdminUser:
        existing = self.get_user_by_username(user_data.username)
        if existing:
            raise UserAlreadyExistsError()
        
        hashed_password = get_password_hash(user_data.password)
        
        user = AdminUser(
            username=user_data.username,
            password_hash=hashed_password,
            role=user_data.role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> AdminUser:
        user = self.get_user_by_id(user_id)
        
        if user_data.password:
            user.password_hash = get_password_hash(user_data.password)
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
        return True
