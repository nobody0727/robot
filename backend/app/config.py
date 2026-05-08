from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "WeChat Bot Admin API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bot_admin:wechat_bot_secure_password_2024@localhost:5432/wechat_bot"
    )
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "your_super_secret_jwt_key_that_should_be_at_least_32_characters_long"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_EMBEDDING_MODEL: str = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "text-embedding-3-small")
    
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    AI_CONTEXT_GROUP: int = int(os.getenv("AI_CONTEXT_GROUP", "10"))
    AI_CONTEXT_PRIVATE: int = int(os.getenv("AI_CONTEXT_PRIVATE", "20"))
    
    MESSAGE_CACHE_TTL: int = int(os.getenv("MESSAGE_CACHE_TTL", "120"))
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
