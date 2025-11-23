from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Dataset(Base):
    """データセットモデル
    
    修正: id, user_idフィールドをUUID型からString型に変更（SQLite互換性のため）
    """
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    rows = Column(Integer, nullable=False)
    columns = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーションシップ
    user = relationship("User", backref="datasets")

