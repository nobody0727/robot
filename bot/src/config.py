import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bot_admin:wechat_bot_secure_password_2024@localhost:5432/wechat_bot"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    WECHATY_TOKEN: str = os.getenv("WECHATY_TOKEN", "")
    WECHATY_PUPPET: str = os.getenv("WECHATY_PUPPET", "wechaty-puppet-donut")
    
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    AI_CONTEXT_GROUP: int = int(os.getenv("AI_CONTEXT_GROUP", "10"))
    AI_CONTEXT_PRIVATE: int = int(os.getenv("AI_CONTEXT_PRIVATE", "20"))
    
    MESSAGE_CACHE_TTL: int = int(os.getenv("MESSAGE_CACHE_TTL", "120"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
