from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Plan(Base):
    """前処理プランモデル
    
    修正: id, user_id, dataset_idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    task_type = Column(String(50), nullable=False)  # classification, regression, clustering
    target_column = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーションシップ
    user = relationship("User", backref="plans")
    dataset = relationship("Dataset", backref="plans")
    steps = relationship("PlanStep", backref="plan", cascade="all, delete-orphan", order_by="PlanStep.order")


class PlanStep(Base):
    """プランステップモデル
    
    修正: id, plan_idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "plan_steps"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("plans.id"), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

