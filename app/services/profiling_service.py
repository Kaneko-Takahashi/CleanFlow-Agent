"""データプロファイリングサービス"""
import pandas as pd
from io import StringIO
from typing import Optional


def profile_csv_data(csv_data: str) -> dict:
    """CSVデータをプロファイリング
    
    Args:
        csv_data: CSV形式の文字列データ
    
    Returns:
        プロファイル情報の辞書
    """
    df = pd.read_csv(StringIO(csv_data))
    return profile_dataframe(df)


def profile_dataframe(df: pd.DataFrame) -> dict:
    """DataFrameをプロファイリング
    
    Args:
        df: 分析対象のDataFrame
    
    Returns:
        プロファイル情報の辞書
    """
    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "missing_rate": float(df.isnull().sum().sum() / (len(df) * len(df.columns))) if len(df) > 0 else 0,
        "numeric_columns": [],
        "categorical_columns": [],
        "datetime_columns": [],
        "column_profiles": {}
    }
    
    for col in df.columns:
        col_profile = _profile_column(df[col])
        profile["column_profiles"][col] = col_profile
        
        # カラムの分類
        if col_profile["dtype_category"] == "numeric":
            profile["numeric_columns"].append(col)
        elif col_profile["dtype_category"] == "datetime":
            profile["datetime_columns"].append(col)
        else:
            profile["categorical_columns"].append(col)
    
    return profile


def _profile_column(series: pd.Series) -> dict:
    """単一カラムをプロファイリング"""
    profile = {
        "dtype": str(series.dtype),
        "dtype_category": _get_dtype_category(series),
        "count": int(series.count()),
        "missing": int(series.isnull().sum()),
        "missing_rate": float(series.isnull().sum() / len(series)) if len(series) > 0 else 0,
        "unique": int(series.nunique()),
        "unique_rate": float(series.nunique() / len(series)) if len(series) > 0 else 0,
    }
    
    # 数値型の場合
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 0:
            profile.update({
                "mean": float(non_null.mean()),
                "std": float(non_null.std()) if len(non_null) > 1 else 0,
                "min": float(non_null.min()),
                "max": float(non_null.max()),
                "median": float(non_null.median()),
                "q1": float(non_null.quantile(0.25)),
                "q3": float(non_null.quantile(0.75)),
            })
            
            # 外れ値の検出（IQR法）
            iqr = profile["q3"] - profile["q1"]
            lower_bound = profile["q1"] - 1.5 * iqr
            upper_bound = profile["q3"] + 1.5 * iqr
            outliers = non_null[(non_null < lower_bound) | (non_null > upper_bound)]
            profile["outliers_count"] = int(len(outliers))
            profile["outliers_rate"] = float(len(outliers) / len(non_null)) if len(non_null) > 0 else 0
    
    # カテゴリ型の場合（ユニーク値が少ない場合）
    if profile["unique"] <= 20 and not pd.api.types.is_numeric_dtype(series):
        value_counts = series.value_counts().head(10).to_dict()
        profile["top_values"] = {str(k): int(v) for k, v in value_counts.items()}
    
    return profile


def _get_dtype_category(series: pd.Series) -> str:
    """データ型のカテゴリを判定"""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif pd.api.types.is_bool_dtype(series):
        return "boolean"
    else:
        return "categorical"


def detect_data_quality_issues(profile: dict) -> list[dict]:
    """データ品質の問題を検出
    
    Args:
        profile: プロファイル情報
    
    Returns:
        検出された問題のリスト
    """
    issues = []
    
    # 欠損値の多いカラム
    for col, col_profile in profile.get("column_profiles", {}).items():
        missing_rate = col_profile.get("missing_rate", 0)
        if missing_rate > 0.5:
            issues.append({
                "type": "high_missing_rate",
                "severity": "high",
                "column": col,
                "message": f"カラム '{col}' の欠損率が {missing_rate:.1%} と高いです",
                "suggestion": "削除または適切な補完を検討してください"
            })
        elif missing_rate > 0.1:
            issues.append({
                "type": "moderate_missing_rate",
                "severity": "medium",
                "column": col,
                "message": f"カラム '{col}' に {missing_rate:.1%} の欠損があります",
                "suggestion": "補完方法を検討してください"
            })
    
    # 外れ値の多いカラム
    for col, col_profile in profile.get("column_profiles", {}).items():
        outliers_rate = col_profile.get("outliers_rate", 0)
        if outliers_rate > 0.1:
            issues.append({
                "type": "high_outliers",
                "severity": "medium",
                "column": col,
                "message": f"カラム '{col}' に {outliers_rate:.1%} の外れ値があります",
                "suggestion": "外れ値の処理を検討してください"
            })
    
    # 高カーディナリティのカテゴリ列
    for col in profile.get("categorical_columns", []):
        col_profile = profile.get("column_profiles", {}).get(col, {})
        unique_rate = col_profile.get("unique_rate", 0)
        if unique_rate > 0.9:
            issues.append({
                "type": "high_cardinality",
                "severity": "low",
                "column": col,
                "message": f"カラム '{col}' のユニーク率が {unique_rate:.1%} と高いです",
                "suggestion": "IDカラムの可能性があります。特徴量として使用する場合は注意してください"
            })
    
    return issues

