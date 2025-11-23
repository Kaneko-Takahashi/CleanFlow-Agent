from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.plan_service import get_user_plans
from app.schemas.plan import PlanListResponse

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=dict)
def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """プラン一覧を取得（ダミー実装）"""
    plans = get_user_plans(db, current_user.id)
    return {
        "data": {
            "plans": [plan.model_dump() for plan in plans],
            "total": len(plans)
        },
        "message": "Success"
    }

