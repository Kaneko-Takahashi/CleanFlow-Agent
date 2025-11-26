"""プロファイリング関連スキーマ"""
from pydantic import BaseModel
from typing import Optional, Any


class ColumnProfile(BaseModel):
    """カラムプロファイル"""
    dtype: str
    dtype_category: str
    count: int
    missing: int
    missing_rate: float
    unique: int
    unique_rate: float
    # 数値型の場合のみ
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    median: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    outliers_count: Optional[int] = None
    outliers_rate: Optional[float] = None
    # カテゴリ型の場合のみ
    top_values: Optional[dict[str, int]] = None


class DataQualityIssue(BaseModel):
    """データ品質の問題"""
    type: str
    severity: str  # high, medium, low
    column: str
    message: str
    suggestion: str


class DatasetProfile(BaseModel):
    """データセットプロファイル"""
    rows: int
    columns: int
    missing_values: int
    missing_rate: float
    numeric_columns: list[str]
    categorical_columns: list[str]
    datetime_columns: list[str]
    column_profiles: dict[str, ColumnProfile]
    quality_issues: Optional[list[DataQualityIssue]] = None


class ProfileRequest(BaseModel):
    """プロファイルリクエスト"""
    csv_data: str

