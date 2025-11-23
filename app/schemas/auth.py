from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """ユーザー登録リクエスト"""
    email: EmailStr = Field(
        ...,
        example="test1@example.com",
        description="ログインに使用するメールアドレス"
    )
    password: str = Field(
        ...,
        min_length=8,
        example="TestPass123!",
        description="8文字以上のパスワード"
    )


class UserLogin(BaseModel):
    """ログインリクエスト"""
    email: EmailStr = Field(
        ...,
        example="test1@example.com",
        description="ログインに使用するメールアドレス"
    )
    password: str = Field(
        ...,
        example="TestPass123!",
        description="パスワード"
    )


class TokenResponse(BaseModel):
    """トークンレスポンス"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

