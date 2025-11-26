# アーキテクチャ設計 - CleanFlow Agent

## システム構成概要

CleanFlow Agent は、FastAPI ベースの RESTful API サーバーとして実装される。認証、データセット管理、前処理プラン生成・実行の各機能をモジュール化し、レイヤードアーキテクチャを採用する。

## コンポーネント構成

### 1. FastAPI アプリケーション層

#### エントリーポイント

- `app/main.py`: FastAPI アプリケーションの初期化、ミドルウェア設定、ルータの登録、例外ハンドラの設定

#### ミドルウェア

- CORS 設定
- リクエストログ記録
- エラーハンドリング

#### 例外ハンドラ

- `ResourceNotFoundException` → 404 Not Found
- `UnauthorizedAccessException` → 403 Forbidden
- `ValidationException` → 400 Bad Request
- `DuplicateResourceException` → 400 Bad Request

### 2. ルータ層（app/routers/）

#### `routers/auth.py`

- 認証関連のエンドポイント
  - `POST /auth/register`: ユーザー登録
  - `POST /auth/login`: ログイン（JSON形式）
  - `POST /auth/token`: OAuth2トークン取得（Swagger用）
  - `GET /auth/me`: 現在のユーザー情報取得
- 依存関係: `dependencies.auth.get_current_user`（JWT トークン検証）

#### `routers/datasets.py`

- データセット関連のエンドポイント
  - `POST /datasets`: データセット作成
  - `GET /datasets`: データセット一覧
- 依存関係: `dependencies.auth.get_current_user`（認証必須）

#### `routers/plans.py`

- 前処理プラン関連のエンドポイント
  - `POST /plans`: プラン作成
  - `GET /plans`: プラン一覧
- 依存関係: `dependencies.auth.get_current_user`（認証必須）

#### `routers/executions.py`

- プラン実行関連のエンドポイント
  - `POST /plans/{plan_id}/execute`: プラン実行
  - `GET /plans/{plan_id}/executions`: プランの実行履歴一覧
  - `GET /executions/{execution_id}`: 実行結果詳細
- 依存関係: `dependencies.auth.get_current_user`（認証必須）

#### `routers/profiling.py`

- データプロファイリング関連のエンドポイント
  - `POST /profiling/analyze`: CSVデータのプロファイリング
- 依存関係: `dependencies.auth.get_current_user`（認証必須）

### 3. 依存性注入層（app/dependencies/）

#### `dependencies/auth.py`

- **機能**:
  - `get_current_user`: JWT トークンからユーザーを取得
  - OAuth2スキーム定義
- **依存**: `repositories.user_repository`, `core.security`

### 4. サービス層（app/services/）

#### `services/auth_service.py`

- **機能**:
  - ユーザー登録処理
  - パスワード検証
  - JWT トークン発行
- **依存**: `repositories.user_repository`, `core.security`
- **例外**: `DuplicateResourceException`, `ValidationException`, `UnauthorizedAccessException`

#### `services/dataset_service.py`

- **機能**:
  - データセット一覧取得
  - データセット作成
- **依存**: `repositories.dataset_repository`

#### `services/plan_service.py`

- **機能**:
  - プラン一覧取得
  - プラン作成（データセット所有権検証付き）
- **依存**: `repositories.plan_repository`, `repositories.dataset_repository`
- **例外**: `ResourceNotFoundException`, `UnauthorizedAccessException`

#### `services/execution_service.py`

- **機能**:
  - プランの実行（各ステップを順次実行）
  - Before/After サマリの計算
  - 実行ログの記録
  - 実行履歴の取得
- **依存**: `repositories.execution_repository`, `repositories.plan_repository`
- **例外**: `ResourceNotFoundException`

#### `services/profiling_service.py`

- **機能**:
  - CSVデータのプロファイリング
  - 各列の統計情報計算（欠損値、ユニーク値、分布等）
  - 外れ値検出（IQR法）
  - データ品質問題の検出

### 5. リポジトリ層（app/repositories/）

#### `repositories/user_repository.py`

- ユーザー情報の CRUD 操作
- `find_by_id`, `find_by_email`, `create`, `exists_by_email`

#### `repositories/dataset_repository.py`

- データセット情報の CRUD 操作
- `find_by_user_id`, `find_by_id`, `find_by_id_and_user`, `create`, `delete`

#### `repositories/plan_repository.py`

- 前処理プラン情報の CRUD 操作
- `find_by_user_id`, `find_by_id`, `find_by_id_and_user`, `create`, `delete`

#### `repositories/execution_repository.py`

- 実行履歴情報の CRUD 操作
- `find_by_id`, `find_by_plan_id`, `create`, `update`, `add_step_log`

### 6. LLM エージェント層（app/agents/）

#### `agents/cleanflow_agent.py`

- **機能**:
  - LLM（Anthropic Claude）を使用した前処理プラン生成
  - システムプロンプトとユーザープロンプトの構築
  - レスポンスのJSONパース
  - APIキー未設定時のダミープラン生成（フォールバック）
- **設定**: `ANTHROPIC_API_KEY`, `LLM_MODEL`, `LLM_MAX_TOKENS`

### 7. 例外層（app/exceptions/）

#### `exceptions/domain_exceptions.py`

- `DomainException`: 基底例外
- `ResourceNotFoundException`: リソースが見つからない（404）
- `UnauthorizedAccessException`: 権限がない（403）
- `ValidationException`: バリデーションエラー（400）
- `DuplicateResourceException`: リソースの重複（400）

### 8. スキーマ層（app/schemas/）

#### 共通レスポンス

- `schemas/responses.py`: `ApiResponse`, `ListData`

#### 認証関連

- `schemas/auth.py`: `UserRegister`, `UserLogin`, `TokenResponse`
- `schemas/user.py`: `UserResponse`

#### データセット関連

- `schemas/dataset.py`: `DatasetCreate`, `DatasetSummary`, `DatasetListResponse`

#### プラン関連

- `schemas/plan.py`: `PlanCreate`, `PlanStep`, `PlanResponse`, `PlanSummary`, `PlanListResponse`

#### 実行関連

- `schemas/execution.py`: `ExecutionResponse`, `ExecutionSummary`, `ExecutionStepLogResponse`, `ExecuteRequest`, `ExecutionListResponse`

#### プロファイリング関連

- `schemas/profiling.py`: `DatasetProfile`, `ColumnProfile`, `DataQualityIssue`, `ProfileRequest`

### 9. モデル層（app/models/）

- `models/user.py`: User モデル
- `models/dataset.py`: Dataset モデル
- `models/plan.py`: Plan, PlanStep モデル
- `models/execution.py`: Execution, ExecutionStepLog モデル

### 10. コア層（app/core/）

#### `core/config.py`

- アプリケーション設定（環境変数から読み込み）
- `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ANTHROPIC_API_KEY`, `LLM_MODEL`, `LLM_MAX_TOKENS`
- `CORS_ORIGINS`

#### `core/security.py`

- パスワードハッシュ化（bcrypt）
- パスワード検証
- JWT トークン生成・検証

## ディレクトリ構造（実装済み）

```
app/
├── __init__.py
├── main.py                    # アプリケーションエントリーポイント
├── agents/
│   ├── __init__.py
│   └── cleanflow_agent.py     # LLM連携プラン生成
├── core/
│   ├── __init__.py
│   ├── config.py              # 設定管理
│   └── security.py            # セキュリティユーティリティ
├── db/
│   ├── __init__.py
│   ├── base.py                # SQLAlchemy Base
│   └── session.py             # DBセッション管理
├── dependencies/
│   ├── __init__.py
│   └── auth.py                # 認証依存性
├── exceptions/
│   ├── __init__.py
│   └── domain_exceptions.py   # ドメイン例外
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── dataset.py
│   ├── plan.py
│   └── execution.py
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py
│   ├── dataset_repository.py
│   ├── plan_repository.py
│   └── execution_repository.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── datasets.py
│   ├── plans.py
│   ├── executions.py
│   └── profiling.py
├── schemas/
│   ├── __init__.py
│   ├── auth.py
│   ├── dataset.py
│   ├── execution.py
│   ├── plan.py
│   ├── profiling.py
│   ├── responses.py
│   └── user.py
└── services/
    ├── __init__.py
    ├── auth_service.py
    ├── dataset_service.py
    ├── execution_service.py
    ├── plan_service.py
    └── profiling_service.py
```

## データフロー

### 1. ユーザー登録・ログインフロー

```
1. クライアント → POST /api/v1/auth/register
2. routers/auth.py → services/auth_service.py
3. auth_service → repositories/user_repository.py
4. user_repository → SQLite（usersテーブルにINSERT）
5. レスポンス返却（ApiResponse形式）
```

### 2. プラン実行フロー

```
1. クライアント → POST /api/v1/plans/{plan_id}/execute
2. routers/executions.py → services/execution_service.py
3. execution_service → repositories/plan_repository.py（プラン取得・権限確認）
4. execution_service → Execution作成（status: running）
5. execution_service → Beforeサマリ計算
6. execution_service → 各ステップを順次実行:
   a. コードスニペットを exec() で実行
   b. ExecutionStepLog を記録
   c. エラー発生時は中断
7. execution_service → Afterサマリ計算
8. execution_service → Execution更新（status: completed/failed）
9. レスポンス返却（ApiResponse形式）
```

### 3. データプロファイリングフロー

```
1. クライアント → POST /api/v1/profiling/analyze
2. routers/profiling.py → services/profiling_service.py
3. profiling_service → pandas（CSV読み込み）
4. profiling_service → 各列のプロファイル計算:
   - データ型判定
   - 欠損値率
   - ユニーク値数
   - 数値列: 平均、標準偏差、四分位数、外れ値
   - カテゴリ列: 頻度分布
5. profiling_service → データ品質問題の検出
6. レスポンス返却（ApiResponse形式）
```

## セキュリティ設計

### 認証・認可

- JWT トークンは環境変数で管理されたシークレットキーで署名
- トークン有効期限: 24 時間（設定可能）
- パスワードは bcrypt でハッシュ化（salt rounds: 12）
- 認証ロジックは `dependencies/auth.py` に集約

### データ分離

- すべてのデータアクセスで user_id をチェック
- リポジトリ層で `find_by_id_and_user` メソッドを提供

### コード実行の安全性

- プランのコードスニペット実行は `exec()` で実行
- 実行環境に `df`（DataFrame）と `pd`（pandas）のみを渡す
- 将来的にサンドボックス環境の強化を検討

## エラーハンドリング

### ドメイン例外からHTTPレスポンスへの変換

| ドメイン例外 | HTTPステータス | 用途 |
|-------------|---------------|------|
| `ResourceNotFoundException` | 404 | リソースが見つからない |
| `UnauthorizedAccessException` | 403 | アクセス権限がない |
| `ValidationException` | 400 | バリデーションエラー |
| `DuplicateResourceException` | 400 | リソースの重複 |

### レスポンス形式

```json
{
  "data": null,
  "message": "エラーメッセージ"
}
```

## 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `DATABASE_URL` | データベース接続文字列 | `sqlite:///./cleanflow.db` |
| `JWT_SECRET_KEY` | JWT署名用シークレット | （要設定） |
| `JWT_ALGORITHM` | JWTアルゴリズム | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | トークン有効期限（分） | `1440`（24時間） |
| `ANTHROPIC_API_KEY` | Anthropic APIキー | `None`（未設定時はダミー生成） |
| `LLM_MODEL` | 使用するLLMモデル | `claude-sonnet-4-20250514` |
| `LLM_MAX_TOKENS` | LLMの最大トークン数 | `4096` |
| `CORS_ORIGINS` | CORS許可オリジン | `["*"]` |

## 依存関係管理

### 主要ライブラリ

- FastAPI: Web フレームワーク
- SQLAlchemy: ORM
- pandas: データ処理
- scikit-learn: 機械学習前処理
- python-jose: JWT 処理
- bcrypt: パスワードハッシュ化
- anthropic: Claude API クライアント
- pydantic-settings: 設定管理
