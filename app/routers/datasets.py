from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.dataset_service import get_user_datasets
from app.schemas.dataset import DatasetListResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=dict)
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """データセット一覧を取得（ダミー実装）"""
    datasets = get_user_datasets(db, current_user.id)
    return {
        "data": {
            "datasets": [dataset.model_dump() for dataset in datasets],
            "total": len(datasets)
        },
        "message": "Success"
    }

