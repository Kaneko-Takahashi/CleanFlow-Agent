"""プランルーター"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.plan_service import get_user_plans, create_plan
from app.schemas.plan import PlanCreate, PlanSummary
from app.schemas.responses import ApiResponse

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=dict)
def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """プラン一覧を取得"""
    plans = get_user_plans(db, current_user.id)
    return ApiResponse.success(
        data={"plans": [p.model_dump() for p in plans], "total": len(plans)}
    ).model_dump()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_plan_endpoint(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規プランを作成"""
    new_plan = create_plan(db, current_user.id, plan_data)
    plan_summary = PlanSummary(
        plan_id=new_plan.id,
        name=new_plan.name,
        dataset_id=new_plan.dataset_id,
        task_type=new_plan.task_type,
        created_at=new_plan.created_at
    )
    return ApiResponse.success(
        data=plan_summary.model_dump(),
        message="Plan created successfully"
    ).model_dump()
