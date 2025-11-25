from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.plan_service import get_user_plans, create_plan
from app.schemas.plan import PlanListResponse, PlanCreate, PlanSummary

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=dict)
def list_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """プラン一覧を取得
    
    現在ログイン中のユーザーのプランのみを返します。
    JWT認証必須です。
    
    実装後の確認手順:
    1. uvicorn app.main:app --reload で起動
    2. Swagger UI (/docs) にアクセス
    3. /api/v1/auth/register → /api/v1/auth/login → /api/v1/auth/token でログイン
    4. GET /api/v1/plans で、ログインユーザーのプラン一覧が取得できることを確認
    """
    plans = get_user_plans(db, current_user.id)
    return {
        "data": {
            "plans": [plan.model_dump() for plan in plans],
            "total": len(plans)
        },
        "message": "Success"
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_plan_endpoint(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規プランを作成
    
    リクエストボディ:
    {
        "dataset_id": "データセットID",
        "task_type": "classification" | "regression" | "clustering",
        "target_column": "ターゲット列名（オプション）",
        "plan_name": "プラン名（オプション）"
    }
    
    ログイン中のユーザーIDを使って plans テーブルに1行INSERTし、
    作成したレコードを返します。
    JWT認証必須です。
    
    実装後の確認手順:
    1. uvicorn app.main:app --reload で起動
    2. Swagger UI (/docs) にアクセス
    3. /api/v1/auth/register → /api/v1/auth/login → /api/v1/auth/token でログイン
    4. POST /api/v1/datasets でデータセットを作成（dataset_idを取得）
    5. POST /api/v1/plans でプランを1件作成
       リクエストボディ例: {
           "dataset_id": "<上記で取得したdataset_id>",
           "task_type": "classification",
           "target_column": "target",
           "plan_name": "テストプラン"
         }
    6. GET /api/v1/plans で作成したプランが一覧に出ることを確認
    """
    new_plan = create_plan(db, current_user.id, plan_data)
    plan_summary = PlanSummary(
        plan_id=new_plan.id,
        name=new_plan.name,
        dataset_id=new_plan.dataset_id,
        task_type=new_plan.task_type,
        created_at=new_plan.created_at
    )
    return {
        "data": plan_summary.model_dump(),
        "message": "Plan created successfully"
    }

