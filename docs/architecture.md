# アーキテクチャ設計 - CleanFlow Agent

## システム構成概要

CleanFlow Agent は、FastAPI ベースの RESTful API サーバーとして実装される。認証、データセット管理、前処理プラン生成・実行の各機能をモジュール化し、レイヤードアーキテクチャを採用する。

## コンポーネント構成

### 1. FastAPI アプリケーション層

#### エントリーポイント

- `main.py`: FastAPI アプリケーションの初期化、ミドルウェア設定、ルータの登録

#### ミドルウェア

- CORS 設定
- リクエストログ記録
- エラーハンドリング

### 2. ルータ層（routers/）

#### `routers/auth.py`

- 認証関連のエンドポイント
  - `POST /auth/register`: ユーザー登録
  - `POST /auth/login`: ログイン
  - `GET /auth/me`: 現在のユーザー情報取得
- 依存関係: `get_current_user`（JWT トークン検証）

#### `routers/datasets.py`

- データセット関連のエンドポイント
  - `POST /datasets`: CSV アップロード
  - `GET /datasets`: データセット一覧
  - `GET /datasets/{dataset_id}`: データセット詳細
  - `GET /datasets/{dataset_id}/profile`: プロファイル取得
  - `DELETE /datasets/{dataset_id}`: データセット削除
- 依存関係: `get_current_user`（認証必須）

#### `routers/plans.py`

- 前処理プラン関連のエンドポイント
  - `POST /datasets/{dataset_id}/plan`: プラン生成
  - `GET /plans`: プラン一覧
  - `GET /plans/{plan_id}`: プラン詳細
  - `POST /plans/{plan_id}/execute`: プラン実行
  - `GET /executions/{execution_id}`: 実行結果詳細
- 依存関係: `get_current_user`（認証必須）

### 3. サービス層（services/）

#### `services/auth_service.py`

- **機能**:
  - ユーザー登録処理
  - パスワードハッシュ化（bcrypt）
  - パスワード検証
  - JWT トークン発行
  - JWT トークン検証
- **依存**: `repositories.user_repository`

#### `services/dataset_service.py`

- **機能**:
  - CSV ファイルの保存
  - データセットの読み込み（pandas）
  - データプロファイルの計算
  - ファイル削除
- **依存**: `repositories.dataset_repository`, `repositories.column_profile_repository`

#### `services/plan_service.py`

- **機能**:
  - LLM へのプロンプト送信
  - 生成された JSON プランのバリデーション
  - プランの保存
- **依存**: `repositories.plan_repository`, `repositories.plan_step_repository`, `cleanflow_agent.llm_client`

#### `services/execution_service.py`

- **機能**:
  - プランの各ステップを順次実行
  - コードスニペットの安全な実行（sandbox 環境）
  - Before/After サマリの計算
  - 実行ログの記録
- **依存**: `repositories.execution_repository`, `repositories.execution_step_log_repository`, `services.dataset_service`

### 4. リポジトリ層（repositories/）

#### `repositories/user_repository.py`

- ユーザー情報の CRUD 操作
- SQLite クエリ実行

#### `repositories/dataset_repository.py`

- データセット情報の CRUD 操作

#### `repositories/column_profile_repository.py`

- 列プロファイル情報の CRUD 操作

#### `repositories/plan_repository.py`

- 前処理プラン情報の CRUD 操作

#### `repositories/plan_step_repository.py`

- プランステップ情報の CRUD 操作

#### `repositories/execution_repository.py`

- 実行履歴情報の CRUD 操作

#### `repositories/execution_step_log_repository.py`

- 実行ステップログ情報の CRUD 操作

#### `repositories/database.py`

- データベース接続管理
- セッション管理
- マイグレーション（Alembic 等を使用）

### 5. LLM エージェント層（cleanflow_agent/）

#### `cleanflow_agent/llm_client.py`

- LLM API（OpenAI 等）への接続
- プロンプトの送信
- レスポンスの取得

#### `cleanflow_agent/prompt_builder.py`

- System Prompt と User Prompt の構築
- データプロファイル情報のフォーマット

#### `cleanflow_agent/response_parser.py`

- LLM レスポンスの JSON パース
- バリデーション

### 6. モデル層（models/）

#### Pydantic モデル（API リクエスト/レスポンス）

- `models/schemas/auth.py`: 認証関連スキーマ
- `models/schemas/dataset.py`: データセット関連スキーマ
- `models/schemas/plan.py`: プラン関連スキーマ
- `models/schemas/execution.py`: 実行関連スキーマ

#### SQLAlchemy モデル（データベース）

- `models/database/user.py`: User モデル
- `models/database/dataset.py`: Dataset モデル
- `models/database/column_profile.py`: ColumnProfile モデル
- `models/database/plan.py`: Plan モデル
- `models/database/plan_step.py`: PlanStep モデル
- `models/database/execution.py`: Execution モデル
- `models/database/execution_step_log.py`: ExecutionStepLog モデル

### 7. ユーティリティ層（utils/）

#### `utils/security.py`

- パスワードハッシュ化・検証
- JWT トークン生成・検証

#### `utils/file_handler.py`

- ファイルアップロード処理
- ファイル削除処理
- ファイルパス管理

#### `utils/validators.py`

- データバリデーション
- ファイル形式チェック

## ディレクトリ構造

```
cleanflow_agent/
├── main.py
├── config.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── datasets.py
│   └── plans.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── dataset_service.py
│   ├── plan_service.py
│   └── execution_service.py
├── repositories/
│   ├── __init__.py
│   ├── database.py
│   ├── user_repository.py
│   ├── dataset_repository.py
│   ├── column_profile_repository.py
│   ├── plan_repository.py
│   ├── plan_step_repository.py
│   ├── execution_repository.py
│   └── execution_step_log_repository.py
├── models/
│   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dataset.py
│   │   ├── plan.py
│   │   └── execution.py
│   └── database/
│       ├── __init__.py
│       ├── user.py
│       ├── dataset.py
│       ├── column_profile.py
│       ├── plan.py
│       ├── plan_step.py
│       ├── execution.py
│       └── execution_step_log.py
├── cleanflow_agent/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── prompt_builder.py
│   └── response_parser.py
├── utils/
│   ├── __init__.py
│   ├── security.py
│   ├── file_handler.py
│   └── validators.py
└── tests/
    ├── __init__.py
    ├── test_auth_service.py
    ├── test_dataset_service.py
    ├── test_plan_service.py
    └── test_execution_service.py
```

## データフロー

### 1. ユーザー登録・ログインフロー

```
1. クライアント → POST /auth/register
2. routers/auth.py → services/auth_service.py
3. auth_service → repositories/user_repository.py
4. user_repository → SQLite（usersテーブルにINSERT）
5. auth_service → JWTトークン生成
6. レスポンス返却（トークン含む）
```

### 2. CSV アップロード・プロファイル生成フロー

```
1. クライアント → POST /datasets (multipart/form-data)
2. routers/datasets.py → services/dataset_service.py
3. dataset_service → utils/file_handler.py（ファイル保存）
4. dataset_service → pandas（CSV読み込み）
5. dataset_service → プロファイル計算
6. dataset_service → repositories/dataset_repository.py（DB保存）
7. dataset_service → repositories/column_profile_repository.py（プロファイル保存）
8. レスポンス返却
```

### 3. 前処理プラン生成フロー

```
1. クライアント → POST /datasets/{dataset_id}/plan
2. routers/plans.py → services/plan_service.py
3. plan_service → services/dataset_service.py（プロファイル取得）
4. plan_service → cleanflow_agent/prompt_builder.py（プロンプト構築）
5. plan_service → cleanflow_agent/llm_client.py（LLM API呼び出し）
6. plan_service → cleanflow_agent/response_parser.py（JSONパース・バリデーション）
7. plan_service → repositories/plan_repository.py（プラン保存）
8. plan_service → repositories/plan_step_repository.py（ステップ保存）
9. レスポンス返却
```

### 4. プラン実行フロー

```
1. クライアント → POST /plans/{plan_id}/execute
2. routers/plans.py → services/execution_service.py
3. execution_service → repositories/plan_repository.py（プラン取得）
4. execution_service → services/dataset_service.py（データセット読み込み）
5. execution_service → Beforeサマリ計算
6. execution_service → 各ステップを順次実行:
   a. コードスニペットを安全に実行（sandbox環境）
   b. 実行結果をログに記録
   c. エラー発生時は中断
7. execution_service → Afterサマリ計算
8. execution_service → repositories/execution_repository.py（実行履歴保存）
9. execution_service → repositories/execution_step_log_repository.py（ログ保存）
10. レスポンス返却
```

## セキュリティ設計

### 認証・認可

- JWT トークンは環境変数で管理されたシークレットキーで署名
- トークン有効期限: 24 時間（設定可能）
- パスワードは bcrypt でハッシュ化（salt rounds: 12）

### データ分離

- すべてのデータアクセスで user_id をチェック
- リポジトリ層で WHERE 句に user_id 条件を必ず含める

### コード実行の安全性

- プランのコードスニペット実行は制限された環境で実行
- 危険な操作（ファイルシステムアクセス、ネットワークアクセス等）を制限
- タイムアウト設定（例: 30 秒）

## エラーハンドリング

### エラーレスポンス形式

- 統一されたエラーレスポンス形式（api_spec.md 参照）
- 適切な HTTP ステータスコード

### ログ記録

- すべてのエラーをログに記録
- スタックトレースを含める
- ログレベル: DEBUG, INFO, WARNING, ERROR

## パフォーマンス考慮事項

### データベース

- インデックス設定（user_id, dataset_id, plan_id 等）
- クエリの最適化

### ファイル処理

- 大きな CSV ファイルはチャンク読み込みを検討
- 非同期処理の検討（将来拡張）

### LLM API 呼び出し

- タイムアウト設定
- リトライロジック（将来拡張）
- レート制限対応（将来拡張）

## 依存関係管理

### 主要ライブラリ

- FastAPI: Web フレームワーク
- SQLAlchemy: ORM
- pandas: データ処理
- scikit-learn: 機械学習前処理
- python-jose: JWT 処理
- passlib: パスワードハッシュ化
- openai: LLM API（または他の LLM ライブラリ）
- pytest: テストフレームワーク

### 環境変数

- `DATABASE_URL`: データベース接続文字列
- `JWT_SECRET_KEY`: JWT 署名用シークレット
- `JWT_ALGORITHM`: JWT アルゴリズム（HS256）
- `OPENAI_API_KEY`: OpenAI API キー（または他の LLM API キー）
- `UPLOAD_DIR`: アップロードファイル保存ディレクトリ
