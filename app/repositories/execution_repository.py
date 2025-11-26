"""実行リポジトリ"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.execution import Execution, ExecutionStepLog


class ExecutionRepository:
    """実行履歴のデータアクセス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, execution_id: str) -> Optional[Execution]:
        """IDで実行履歴を取得"""
        return self.db.query(Execution).filter(Execution.id == execution_id).first()
    
    def find_by_plan_id(self, plan_id: str) -> List[Execution]:
        """プランIDで実行履歴一覧を取得（作成日時降順）"""
        return self.db.query(Execution).filter(
            Execution.plan_id == plan_id
        ).order_by(Execution.created_at.desc()).all()
    
    def create(self, execution: Execution) -> Execution:
        """実行履歴を作成"""
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def update(self, execution: Execution) -> Execution:
        """実行履歴を更新"""
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def add_step_log(self, step_log: ExecutionStepLog) -> ExecutionStepLog:
        """ステップログを追加"""
        self.db.add(step_log)
        self.db.commit()
        self.db.refresh(step_log)
        return step_log

