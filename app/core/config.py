from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./cleanflow.db"
    
    # JWT設定
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間
    
    # CORS設定
    CORS_ORIGINS: list[str] = ["*"]
    
    # LLM設定
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
