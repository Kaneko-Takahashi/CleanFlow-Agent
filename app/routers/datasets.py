"""データセットルーター"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.dataset_service import get_user_datasets, create_dataset
from app.schemas.dataset import DatasetCreate, DatasetSummary
from app.schemas.responses import ApiResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


class DatasetListData:
    """データセット一覧レスポンスデータ"""
    def __init__(self, datasets: list[DatasetSummary], total: int):
        self.datasets = datasets
        self.total = total


@router.get("", response_model=dict)
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """データセット一覧を取得"""
    datasets = get_user_datasets(db, current_user.id)
    return ApiResponse.success(
        data={"datasets": [d.model_dump() for d in datasets], "total": len(datasets)}
    ).model_dump()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_dataset_endpoint(
    dataset_data: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新規データセットを作成"""
    new_dataset = create_dataset(db, current_user.id, dataset_data)
    dataset_summary = DatasetSummary(
        dataset_id=new_dataset.id,
        name=new_dataset.name,
        description=new_dataset.description,
        created_at=new_dataset.created_at
    )
    return ApiResponse.success(
        data=dataset_summary.model_dump(),
        message="Dataset created successfully"
    ).model_dump()
