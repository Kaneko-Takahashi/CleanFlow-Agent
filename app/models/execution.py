from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Execution(Base):
    """プラン実行履歴モデル
    
    修正: id, plan_idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "executions"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("plans.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    before_summary_json = Column(Text, nullable=True)
    after_summary_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ
    plan = relationship("Plan", backref="executions")
    step_logs = relationship("ExecutionStepLog", backref="execution", cascade="all, delete-orphan", order_by="ExecutionStepLog.step_order")


class ExecutionStepLog(Base):
    """実行ステップログモデル
    
    修正: id, execution_idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "execution_step_logs"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed
    execution_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

