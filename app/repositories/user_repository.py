"""ユーザーリポジトリ"""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User


class UserRepository:
    """ユーザーのデータアクセス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """IDでユーザーを取得"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def find_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user: User) -> User:
        """ユーザーを作成"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def exists_by_email(self, email: str) -> bool:
        """メールアドレスが既に存在するか確認"""
        return self.db.query(User).filter(User.email == email).first() is not None

