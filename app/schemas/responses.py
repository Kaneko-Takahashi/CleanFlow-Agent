"""共通レスポンススキーマ"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API共通レスポンス"""
    data: T
    message: str
    
    @classmethod
    def success(cls, data: T, message: str = "Success") -> "ApiResponse[T]":
        return cls(data=data, message=message)


class ListData(BaseModel, Generic[T]):
    """リスト形式のデータ"""
    items: list[T]
    total: int

