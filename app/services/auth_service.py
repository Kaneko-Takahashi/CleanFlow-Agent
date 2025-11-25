from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.user import UserResponse


def register_user(db: Session, user_data: UserRegister) -> UserResponse:
    """ユーザーを登録"""
    # メールアドレスの重複チェック
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )
    
    # パスワード強度チェック（最低8文字）
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスワードは8文字以上である必要があります"
        )
    
    # パスワードのバイト長チェック（bcryptの72バイト制限）
    password_bytes = user_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスワードが長すぎます（72バイト以下である必要があります）"
        )
    
    # ユーザーを作成
    try:
        hashed_password = get_password_hash(user_data.password)
    except ValueError as e:
        # bcrypt関連のエラーをキャッチ
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"パスワードのハッシュ化に失敗しました: {str(e)}"
        )
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        user_id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at
    )


def authenticate_user(db: Session, email: str, password: str) -> TokenResponse:
    """ユーザーを認証してトークンを返す（共通認証ロジック）"""
    # ユーザーを検索
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
    # パスワードを検証
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
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

