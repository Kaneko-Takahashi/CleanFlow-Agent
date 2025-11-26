"""プロファイリングルーター"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.profiling_service import profile_csv_data, detect_data_quality_issues
from app.schemas.profiling import ProfileRequest, DatasetProfile, DataQualityIssue, ColumnProfile
from app.schemas.responses import ApiResponse

router = APIRouter(prefix="/profiling", tags=["profiling"])


@router.post("/analyze", response_model=dict)
def analyze_data(
    request: ProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """CSVデータをプロファイリング
    
    CSVデータを分析し、統計情報と品質問題を返します。
    """
    profile = profile_csv_data(request.csv_data)
    issues = detect_data_quality_issues(profile)
    
    # レスポンス用に変換
    column_profiles = {
        col: ColumnProfile(**data) 
        for col, data in profile.get("column_profiles", {}).items()
    }
    
    quality_issues = [DataQualityIssue(**issue) for issue in issues]
    
    response = DatasetProfile(
        rows=profile["rows"],
        columns=profile["columns"],
        missing_values=profile["missing_values"],
        missing_rate=profile["missing_rate"],
        numeric_columns=profile["numeric_columns"],
        categorical_columns=profile["categorical_columns"],
        datetime_columns=profile["datetime_columns"],
        column_profiles=column_profiles,
        quality_issues=quality_issues
    )
    
    return ApiResponse.success(data=response.model_dump()).model_dump()

