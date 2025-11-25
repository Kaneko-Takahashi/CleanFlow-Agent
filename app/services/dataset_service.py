from sqlalchemy.orm import Session
from typing import List
import uuid

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetSummary, DatasetCreate


def get_user_datasets(db: Session, user_id: str) -> List[DatasetSummary]:
    """ユーザーのデータセット一覧を取得"""
    datasets = db.query(Dataset).filter(Dataset.user_id == user_id).order_by(Dataset.created_at.desc()).all()
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
    new_dataset = Dataset(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=dataset_data.name,
        description=dataset_data.description
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    return new_dataset

