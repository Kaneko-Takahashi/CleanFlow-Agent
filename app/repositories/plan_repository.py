"""プランリポジトリ"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.plan import Plan


class PlanRepository:
    """プランのデータアクセス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_user_id(self, user_id: str) -> List[Plan]:
        """ユーザーIDでプラン一覧を取得（作成日時降順）"""
        return self.db.query(Plan).filter(
            Plan.user_id == user_id
        ).order_by(Plan.created_at.desc()).all()
    
    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        """IDでプランを取得"""
        return self.db.query(Plan).filter(Plan.id == plan_id).first()
    
    def find_by_id_and_user(self, plan_id: str, user_id: str) -> Optional[Plan]:
        """IDとユーザーIDでプランを取得"""
        return self.db.query(Plan).filter(
            Plan.id == plan_id,
            Plan.user_id == user_id
        ).first()
    
    def create(self, plan: Plan) -> Plan:
        """プランを作成"""
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def delete(self, plan: Plan) -> None:
        """プランを削除"""
        self.db.delete(plan)
        self.db.commit()

