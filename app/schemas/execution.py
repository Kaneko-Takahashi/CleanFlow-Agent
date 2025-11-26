"""実行関連スキーマ"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class ExecutionSummary(BaseModel):
    """実行サマリ（Before/After）"""
    rows: int
    columns: int
    missing_values: int
    column_info: Optional[dict[str, Any]] = None


class ExecutionStepLogResponse(BaseModel):
    """実行ステップログレスポンス"""
    order: int
    name: str
    status: str  # success, failed
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """実行レスポンス"""
    execution_id: str
    plan_id: str
    status: str  # pending, running, completed, failed
    before_summary: Optional[ExecutionSummary] = None
    after_summary: Optional[ExecutionSummary] = None
    step_logs: list[ExecutionStepLogResponse] = []
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """実行履歴一覧レスポンス"""
    executions: list[ExecutionResponse]
    total: int


class ExecuteRequest(BaseModel):
    """実行リクエスト"""
    csv_data: Optional[str] = None  # CSVデータ（オプション）
