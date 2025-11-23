from sqlalchemy.orm import Session
from typing import List

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetSummary


def get_user_datasets(db: Session, user_id: str) -> List[DatasetSummary]:
    """ユーザーのデータセット一覧を取得（ダミー実装）"""
    # 後で実装するため、今は空のリストを返す
    return []

