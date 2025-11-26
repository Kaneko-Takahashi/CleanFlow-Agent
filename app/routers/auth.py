"""認証ルーター"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.dependencies.auth import get_current_user
from app.services.auth_service import register_user, login_user, authenticate_user
from app.schemas.responses import ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """ユーザー登録"""
    user = register_user(db, user_data)
    return ApiResponse.success(
        data={
            "user_id": str(user.user_id),
            "email": user.email,
            "created_at": user.created_at.isoformat()
        },
        message="User registered successfully"
    ).model_dump()


@router.post("/login", response_model=dict)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """ログイン（JSON リクエスト用）"""
    token_response = login_user(db, login_data)
    return ApiResponse.success(
        data={
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in
        },
        message="Login successful"
    ).model_dump()


@router.post("/token", response_model=TokenResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 トークン取得（Swagger Authorize 用）"""
    token_response = authenticate_user(db, form_data.username, form_data.password)
    return token_response


@router.get("/me", response_model=dict)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """現在のユーザー情報を取得"""
    return ApiResponse.success(
        data={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat()
        }
    ).model_dump()
