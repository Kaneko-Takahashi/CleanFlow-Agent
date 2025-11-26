"""実行ルーター"""
import json
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.execution_service import execute_plan, get_execution, get_plan_executions
from app.schemas.execution import (
    ExecutionResponse,
    ExecutionSummary,
    ExecutionStepLogResponse,
    ExecuteRequest,
)
from app.schemas.responses import ApiResponse

router = APIRouter(prefix="/plans", tags=["executions"])


def _execution_to_response(execution) -> ExecutionResponse:
    """Executionモデルをレスポンスに変換"""
    before_summary = None
    after_summary = None
    
    if execution.before_summary_json:
        before_data = json.loads(execution.before_summary_json)
        before_summary = ExecutionSummary(**before_data)
    
    if execution.after_summary_json:
        after_data = json.loads(execution.after_summary_json)
        after_summary = ExecutionSummary(**after_data)
    
    step_logs = [
        ExecutionStepLogResponse(
            order=log.step_order,
            name=log.step_name,
            status=log.status,
            execution_time=log.execution_time,
            error_message=log.error_message
        )
        for log in execution.step_logs
    ]
    
    return ExecutionResponse(
        execution_id=execution.id,
        plan_id=execution.plan_id,
        status=execution.status,
        before_summary=before_summary,
        after_summary=after_summary,
        step_logs=step_logs,
        execution_time=execution.execution_time,
        error_message=execution.error_message,
        created_at=execution.created_at,
        completed_at=execution.completed_at
    )


@router.post("/{plan_id}/execute", response_model=dict, status_code=status.HTTP_201_CREATED)
def execute_plan_endpoint(
    plan_id: str,
    request: ExecuteRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """プランを実行
    
    指定されたプランを実行し、実行履歴を返します。
    オプションでCSVデータを渡すことができます。
    """
    csv_data = request.csv_data if request else None
    execution = execute_plan(db, plan_id, current_user.id, csv_data)
    response = _execution_to_response(execution)
    return ApiResponse.success(
        data=response.model_dump(),
        message="Plan executed successfully" if execution.status == "completed" else "Plan execution failed"
    ).model_dump()


@router.get("/{plan_id}/executions", response_model=dict)
def list_plan_executions(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """プランの実行履歴一覧を取得"""
    executions = get_plan_executions(db, plan_id, current_user.id)
    responses = [_execution_to_response(e) for e in executions]
    return ApiResponse.success(
        data={
            "executions": [r.model_dump() for r in responses],
            "total": len(responses)
        }
    ).model_dump()


# 別のルーターで実行詳細を取得
execution_detail_router = APIRouter(prefix="/executions", tags=["executions"])


@execution_detail_router.get("/{execution_id}", response_model=dict)
def get_execution_detail(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """実行履歴の詳細を取得"""
    execution = get_execution(db, execution_id)
    response = _execution_to_response(execution)
    return ApiResponse.success(data=response.model_dump()).model_dump()

