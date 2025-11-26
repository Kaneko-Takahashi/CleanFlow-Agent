"""データセットリポジトリ"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.dataset import Dataset


class DatasetRepository:
    """データセットのデータアクセス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_user_id(self, user_id: str) -> List[Dataset]:
        """ユーザーIDでデータセット一覧を取得（作成日時降順）"""
        return self.db.query(Dataset).filter(
            Dataset.user_id == user_id
        ).order_by(Dataset.created_at.desc()).all()
    
    def find_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """IDでデータセットを取得"""
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    def find_by_id_and_user(self, dataset_id: str, user_id: str) -> Optional[Dataset]:
        """IDとユーザーIDでデータセットを取得"""
        return self.db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()
    
    def create(self, dataset: Dataset) -> Dataset:
        """データセットを作成"""
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset
    
    def delete(self, dataset: Dataset) -> None:
        """データセットを削除"""
        self.db.delete(dataset)
        self.db.commit()

