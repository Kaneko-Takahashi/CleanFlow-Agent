from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DatasetCreate(BaseModel):
    """データセット作成リクエスト"""
    name: str
    description: Optional[str] = None


class DatasetSummary(BaseModel):
    """データセットサマリ"""
    dataset_id: str  # UUIDを文字列として扱う（SQLite互換性のため）
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    """データセット一覧レスポンス"""
    datasets: list[DatasetSummary]
    total: int

