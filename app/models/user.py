from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class User(Base):
    """ユーザーモデル
    
    修正: idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

