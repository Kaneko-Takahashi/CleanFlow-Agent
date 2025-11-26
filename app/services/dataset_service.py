"""データセットサービス"""
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetSummary, DatasetCreate
from app.repositories.dataset_repository import DatasetRepository


def get_user_datasets(db: Session, user_id: str) -> List[DatasetSummary]:
    """ユーザーのデータセット一覧を取得"""
    repo = DatasetRepository(db)
    datasets = repo.find_by_user_id(user_id)
    return [
        DatasetSummary(
            dataset_id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            created_at=dataset.created_at
        )
        for dataset in datasets
    ]


def create_dataset(db: Session, user_id: str, dataset_data: DatasetCreate) -> Dataset:
    """新規データセットを作成"""
    repo = DatasetRepository(db)
    new_dataset = Dataset(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=dataset_data.name,
        description=dataset_data.description
    )
    return repo.create(new_dataset)
