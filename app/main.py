from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers import auth, datasets, plans

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

# ルーターを登録
app.include_router(auth.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

