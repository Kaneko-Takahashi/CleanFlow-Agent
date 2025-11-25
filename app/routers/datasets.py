from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.dataset_service import get_user_datasets, create_dataset
from app.schemas.dataset import DatasetListResponse, DatasetCreate, DatasetSummary

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=dict)
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """データセット一覧を取得
    
    現在ログイン中のユーザーのデータセットのみを返します。
    JWT認証必須です。
    
    実装後の確認手順:
    1. Swagger UI (/docs) にアクセス
    2. Authorize ボタンから /api/v1/auth/token で認証
    3. GET /api/v1/datasets を実行してデータセット一覧を取得
    """
    datasets = get_user_datasets(db, current_user.id)
    return {
        "data": {
            "datasets": [dataset.model_dump() for dataset in datasets],
            "total": len(datasets)
        },
        "message": "Success"
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_dataset_endpoint(
    dataset_data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規データセットを作成
    
    リクエストボディ:
    {
        "name": "データセット名",
        "description": "説明（任意）"
    }
    
    ログイン中のユーザーIDを使って datasets テーブルに1行INSERTし、
    作成したレコードを返します。
    JWT認証必須です。
    
    実装後の確認手順:
    1. Swagger UI (/docs) にアクセス
    2. Authorize ボタンから /api/v1/auth/token で認証
    3. POST /api/v1/datasets を実行してデータセットを作成
       リクエストボディ例: {"name": "テストデータセット", "description": "説明"}
    4. GET /api/v1/datasets で作成したデータが一覧に出ることを確認
    """
    new_dataset = create_dataset(db, current_user.id, dataset_data)
    dataset_summary = DatasetSummary(
        dataset_id=new_dataset.id,
        name=new_dataset.name,
        description=new_dataset.description,
        created_at=new_dataset.created_at
    )
    return {
        "data": dataset_summary.model_dump(),
        "message": "Dataset created successfully"
    }

