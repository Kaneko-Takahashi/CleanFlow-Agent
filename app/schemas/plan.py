from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class PlanStep(BaseModel):
    """プランステップ"""
    order: int
    name: str
    description: Optional[str] = None
    code_snippet: str
    
    class Config:
        from_attributes = True


class PlanCreate(BaseModel):
    """プラン作成リクエスト"""
    dataset_id: str  # 関連するデータセットID
    task_type: str  # classification, regression, clustering
    target_column: Optional[str] = None
    plan_name: Optional[str] = None


class PlanResponse(BaseModel):
    """プランレスポンス"""
    plan_id: str  # UUIDを文字列として扱う（SQLite互換性のため）
    dataset_id: str
    task_type: str
    target_column: Optional[str]
    name: Optional[str]
    steps: list[PlanStep]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlanSummary(BaseModel):
    """プランサマリ"""
    plan_id: str  # UUIDを文字列として扱う（SQLite互換性のため）
    name: Optional[str]
    dataset_id: str
    task_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """プラン一覧レスポンス"""
    plans: list[PlanSummary]
    total: int

