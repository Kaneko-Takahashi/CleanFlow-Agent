"""プランサービス"""
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.models.plan import Plan
from app.schemas.plan import PlanSummary, PlanCreate
from app.repositories.plan_repository import PlanRepository
from app.repositories.dataset_repository import DatasetRepository
from app.exceptions import ResourceNotFoundException, UnauthorizedAccessException


def get_user_plans(db: Session, user_id: str) -> List[PlanSummary]:
    """ユーザーのプラン一覧を取得"""
    repo = PlanRepository(db)
    plans = repo.find_by_user_id(user_id)
    return [
        PlanSummary(
            plan_id=plan.id,
            name=plan.name,
            dataset_id=plan.dataset_id,
            task_type=plan.task_type,
            created_at=plan.created_at
        )
        for plan in plans
    ]


def create_plan(db: Session, user_id: str, plan_in: PlanCreate) -> Plan:
    """新規プランを作成"""
    dataset_repo = DatasetRepository(db)
    plan_repo = PlanRepository(db)
    
    # データセットの存在確認
    dataset = dataset_repo.find_by_id(plan_in.dataset_id)
    if not dataset:
        raise ResourceNotFoundException("Dataset", plan_in.dataset_id)
    
    # 所有権確認
    if dataset.user_id != user_id:
        raise UnauthorizedAccessException("このデータセットへのアクセス権限がありません")
    
    # プランを作成
    new_plan = Plan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        dataset_id=plan_in.dataset_id,
        name=plan_in.plan_name,
        task_type=plan_in.task_type,
        target_column=plan_in.target_column
    )
    return plan_repo.create(new_plan)
