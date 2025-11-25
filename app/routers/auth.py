from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.user import UserResponse
from app.core.security import get_current_user
from app.services.auth_service import register_user, login_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """ユーザー登録"""
    user = register_user(db, user_data)
    return {
        "data": {
            "user_id": str(user.user_id),
            "email": user.email,
            "created_at": user.created_at.isoformat()
        },
        "message": "User registered successfully"
    }


@router.post("/login", response_model=dict)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """ログイン（JSON リクエスト用）"""
    token_response = login_user(db, login_data)
    return {
        "data": {
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in
        },
        "message": "Login successful"
    }


@router.post("/token", response_model=TokenResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 トークン取得（Swagger Authorize 用）"""
    # form_data.username を email として扱う
    token_response = authenticate_user(db, form_data.username, form_data.password)
    return token_response


@router.get("/me", response_model=dict)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """現在のユーザー情報を取得"""
    return {
        "data": {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat()
        },
        "message": "Success"
    }

