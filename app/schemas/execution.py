from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Any


class ExecutionSummary(BaseModel):
    """実行サマリ（Before/After）"""
    rows: int
    columns: int
    missing_values: int
    # その他の統計量は任意のJSONとして扱う
    statistics: Optional[dict[str, Any]] = None


class ExecutionStepLog(BaseModel):
    """実行ステップログ"""
    order: int
    name: str
    status: str  # success, failed
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """実行レスポンス"""
    execution_id: UUID
    plan_id: UUID
    status: str  # pending, running, completed, failed
    before: ExecutionSummary
    after: Optional[ExecutionSummary] = None
    steps: list[ExecutionStepLog]
    created_at: datetime
    
    class Config:
        from_attributes = True

