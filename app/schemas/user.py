from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """ユーザーレスポンス"""
    user_id: UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

