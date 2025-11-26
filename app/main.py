from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers import auth, datasets, plans, executions
from app.routers import profiling
from app.exceptions import (
    ResourceNotFoundException,
    UnauthorizedAccessException,
    ValidationException,
    DuplicateResourceException,
)

# データベーステーブルを作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリを作成
app = FastAPI(
    title="CleanFlow Agent API",
    description="CSVデータの前処理を自動化するAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ドメイン例外ハンドラー
@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"data": None, "message": str(exc)}
    )


@app.exception_handler(UnauthorizedAccessException)
async def unauthorized_access_handler(request: Request, exc: UnauthorizedAccessException):
    return JSONResponse(
        status_code=403,
        content={"data": None, "message": str(exc)}
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={"data": None, "message": str(exc)}
    )


@app.exception_handler(DuplicateResourceException)
async def duplicate_resource_handler(request: Request, exc: DuplicateResourceException):
    return JSONResponse(
        status_code=400,
        content={"data": None, "message": str(exc)}
    )


# ルーターを登録
app.include_router(auth.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")
app.include_router(executions.execution_detail_router, prefix="/api/v1")
app.include_router(profiling.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
