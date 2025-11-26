"""認証サービス"""
from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.user import UserResponse
from app.repositories.user_repository import UserRepository
from app.exceptions import DuplicateResourceException, ValidationException, UnauthorizedAccessException


def register_user(db: Session, user_data: UserRegister) -> UserResponse:
    """ユーザーを登録"""
    repo = UserRepository(db)
    
    # メールアドレスの重複チェック
    if repo.exists_by_email(user_data.email):
        raise DuplicateResourceException("User", user_data.email)
    
    # パスワード強度チェック（最低8文字）
    if len(user_data.password) < 8:
        raise ValidationException("パスワードは8文字以上である必要があります")
    
    # パスワードのバイト長チェック（bcryptの72バイト制限）
    password_bytes = user_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValidationException("パスワードが長すぎます（72バイト以下である必要があります）")
    
    # ユーザーを作成
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    created_user = repo.create(new_user)
    
    return UserResponse(
        user_id=created_user.id,
        email=created_user.email,
        created_at=created_user.created_at
    )


def authenticate_user(db: Session, email: str, password: str) -> TokenResponse:
    """ユーザーを認証してトークンを返す"""
    repo = UserRepository(db)
    
    user = repo.find_by_email(email)
    if not user:
        raise UnauthorizedAccessException("メールアドレスまたはパスワードが正しくありません")
    
    if not verify_password(password, user.password_hash):
        raise UnauthorizedAccessException("メールアドレスまたはパスワードが正しくありません")
    
    # JWTトークンを生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def login_user(db: Session, login_data: UserLogin) -> TokenResponse:
    """ユーザーをログイン（JSON リクエスト用）"""
    return authenticate_user(db, login_data.email, login_data.password)
