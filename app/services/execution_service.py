"""実行サービス"""
import json
import time
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO

from app.models.execution import Execution, ExecutionStepLog
from app.models.plan import Plan
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.plan_repository import PlanRepository
from app.exceptions import ResourceNotFoundException


def generate_data_summary(df: pd.DataFrame) -> dict:
    """データフレームのサマリを生成"""
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "column_info": {}
    }
    
    for col in df.columns:
        col_info = {
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isnull().sum()),
            "unique": int(df[col].nunique())
        }
        
        # 数値列の場合は統計情報を追加
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
            col_info["std"] = float(df[col].std()) if not df[col].isnull().all() else None
            col_info["min"] = float(df[col].min()) if not df[col].isnull().all() else None
            col_info["max"] = float(df[col].max()) if not df[col].isnull().all() else None
        
        summary["column_info"][col] = col_info
    
    return summary


def execute_plan(db: Session, plan_id: str, user_id: str, csv_data: Optional[str] = None) -> Execution:
    """プランを実行
    
    Args:
        db: データベースセッション
        plan_id: 実行するプランのID
        user_id: 実行ユーザーのID
        csv_data: CSVデータ（文字列形式）。Noneの場合はサンプルデータを使用
    
    Returns:
        実行履歴
    """
    plan_repo = PlanRepository(db)
    exec_repo = ExecutionRepository(db)
    
    # プランの取得と権限確認
    plan = plan_repo.find_by_id_and_user(plan_id, user_id)
    if not plan:
        raise ResourceNotFoundException("Plan", plan_id)
    
    # 実行履歴を作成
    execution = Execution(
        id=str(uuid.uuid4()),
        plan_id=plan_id,
        status="running"
    )
    exec_repo.create(execution)
    
    # データフレームを準備
    if csv_data:
        df = pd.read_csv(StringIO(csv_data))
    else:
        # サンプルデータを生成
        df = _generate_sample_data()
    
    # Before サマリを記録
    before_summary = generate_data_summary(df)
    execution.before_summary_json = json.dumps(before_summary, ensure_ascii=False)
    
    total_start_time = time.time()
    error_occurred = False
    
    # 各ステップを実行
    for step in plan.steps:
        step_start_time = time.time()
        step_log = ExecutionStepLog(
            id=str(uuid.uuid4()),
            execution_id=execution.id,
            step_order=step.order,
            step_name=step.name,
            status="running"
        )
        
        try:
            # コードスニペットを実行
            exec_globals = {"df": df, "pd": pd}
            exec(step.code_snippet, exec_globals)
            df = exec_globals.get("df", df)
            
            step_log.status = "success"
            step_log.execution_time = time.time() - step_start_time
            
        except Exception as e:
            step_log.status = "failed"
            step_log.error_message = str(e)
            step_log.execution_time = time.time() - step_start_time
            error_occurred = True
            exec_repo.add_step_log(step_log)
            break
        
        exec_repo.add_step_log(step_log)
    
    # After サマリを記録
    after_summary = generate_data_summary(df)
    execution.after_summary_json = json.dumps(after_summary, ensure_ascii=False)
    
    # 実行結果を更新
    execution.status = "failed" if error_occurred else "completed"
    execution.execution_time = time.time() - total_start_time
    execution.completed_at = datetime.utcnow()
    
    exec_repo.update(execution)
    
    return execution


def get_execution(db: Session, execution_id: str) -> Execution:
    """実行履歴を取得"""
    exec_repo = ExecutionRepository(db)
    execution = exec_repo.find_by_id(execution_id)
    if not execution:
        raise ResourceNotFoundException("Execution", execution_id)
    return execution


def get_plan_executions(db: Session, plan_id: str, user_id: str) -> list[Execution]:
    """プランの実行履歴一覧を取得"""
    plan_repo = PlanRepository(db)
    exec_repo = ExecutionRepository(db)
    
    # プランの存在と権限確認
    plan = plan_repo.find_by_id_and_user(plan_id, user_id)
    if not plan:
        raise ResourceNotFoundException("Plan", plan_id)
    
    return exec_repo.find_by_plan_id(plan_id)


def _generate_sample_data() -> pd.DataFrame:
    """サンプルデータを生成"""
    import numpy as np
    
    np.random.seed(42)
    n_samples = 100
    
    data = {
        "age": np.random.randint(18, 80, n_samples),
        "income": np.random.normal(50000, 15000, n_samples),
        "category": np.random.choice(["A", "B", "C"], n_samples),
        "score": np.random.uniform(0, 100, n_samples),
        "target": np.random.choice([0, 1], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # 欠損値を追加
    mask = np.random.random(n_samples) < 0.1
    df.loc[mask, "income"] = np.nan
    
    return df
