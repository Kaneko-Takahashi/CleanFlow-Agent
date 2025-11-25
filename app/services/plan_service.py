from sqlalchemy.orm import Session
from typing import List
import uuid
from fastapi import HTTPException, status

from app.models.plan import Plan
from app.models.dataset import Dataset
from app.schemas.plan import PlanSummary, PlanCreate


def get_user_plans(db: Session, user_id: str) -> List[PlanSummary]:
    """ユーザーのプラン一覧を取得
    
    指定ユーザーの plans を新しい順（created_at DESC）で取得し、リストを返す。
    """
    plans = db.query(Plan).filter(Plan.user_id == user_id).order_by(Plan.created_at.desc()).all()
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
    """新規プランを作成
    
    指定ユーザーの plan を1件作成し、保存したモデルインスタンスを返す。
    dataset_idが存在するか、かつそのデータセットがユーザー所有であることを確認する。
    """
    # データセットの存在確認と所有権確認
    dataset = db.query(Dataset).filter(
        Dataset.id == plan_in.dataset_id,
        Dataset.user_id == user_id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="データセットが見つからないか、アクセス権限がありません"
        )
    
    # プランを作成
    new_plan = Plan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        dataset_id=plan_in.dataset_id,
        name=plan_in.plan_name,
        task_type=plan_in.task_type,
        target_column=plan_in.target_column
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

