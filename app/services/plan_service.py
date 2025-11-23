from sqlalchemy.orm import Session
from typing import List

from app.schemas.plan import PlanSummary


def get_user_plans(db: Session, user_id: str) -> List[PlanSummary]:
    """ユーザーのプラン一覧を取得（ダミー実装）"""
    # 後で実装するため、今は空のリストを返す
    return []

