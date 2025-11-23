# データモデル定義 - CleanFlow Agent

## データベーステーブル定義

### users テーブル

ユーザー情報を格納するテーブル。

| カラム名      | 型           | 制約                                | 説明                       |
| ------------- | ------------ | ----------------------------------- | -------------------------- |
| id            | UUID         | PRIMARY KEY                         | ユーザー ID（UUID）        |
| email         | VARCHAR(255) | UNIQUE, NOT NULL                    | メールアドレス             |
| password_hash | VARCHAR(255) | NOT NULL                            | ハッシュ化されたパスワード |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                   |
| updated_at    | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新日時                   |

### datasets テーブル

アップロードされたデータセット情報を格納するテーブル。

| カラム名   | 型           | 制約                                | 説明                    |
| ---------- | ------------ | ----------------------------------- | ----------------------- |
| id         | UUID         | PRIMARY KEY                         | データセット ID（UUID） |
| user_id    | UUID         | FOREIGN KEY (users.id), NOT NULL    | 所有者のユーザー ID     |
| name       | VARCHAR(255) | NOT NULL                            | データセット名          |
| file_path  | VARCHAR(500) | NOT NULL                            | CSV ファイルの保存パス  |
| rows       | INTEGER      | NOT NULL                            | 行数                    |
| columns    | INTEGER      | NOT NULL                            | 列数                    |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                |
| updated_at | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新日時                |

**インデックス**: `user_id`（ユーザーごとのデータセット検索を高速化）

### column_profiles テーブル

データセットの各列のプロファイル情報を格納するテーブル。

| カラム名        | 型           | 制約                                | 説明                                                     |
| --------------- | ------------ | ----------------------------------- | -------------------------------------------------------- |
| id              | UUID         | PRIMARY KEY                         | プロファイル ID（UUID）                                  |
| dataset_id      | UUID         | FOREIGN KEY (datasets.id), NOT NULL | データセット ID                                          |
| column_name     | VARCHAR(255) | NOT NULL                            | 列名                                                     |
| dtype           | VARCHAR(50)  | NOT NULL                            | データ型（int64, float64, object 等）                    |
| missing_count   | INTEGER      | NOT NULL, DEFAULT 0                 | 欠損値の数                                               |
| missing_rate    | FLOAT        | NOT NULL, DEFAULT 0.0               | 欠損率（0.0-1.0）                                        |
| unique_count    | INTEGER      | NOT NULL                            | ユニーク値の数                                           |
| statistics_json | TEXT         | NULL                                | 基本統計量を JSON 形式で保存（平均、中央値、標準偏差等） |
| created_at      | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                                                 |

**インデックス**: `dataset_id`（データセットごとのプロファイル検索を高速化）

**ユニーク制約**: `(dataset_id, column_name)`（同じデータセット内で列名は一意）

### plans テーブル

生成された前処理プラン情報を格納するテーブル。

| カラム名      | 型           | 制約                                | 説明                                                 |
| ------------- | ------------ | ----------------------------------- | ---------------------------------------------------- |
| id            | UUID         | PRIMARY KEY                         | プラン ID（UUID）                                    |
| user_id       | UUID         | FOREIGN KEY (users.id), NOT NULL    | 所有者のユーザー ID                                  |
| dataset_id    | UUID         | FOREIGN KEY (datasets.id), NOT NULL | 関連するデータセット ID                              |
| name          | VARCHAR(255) | NULL                                | プラン名（オプション）                               |
| task_type     | VARCHAR(50)  | NOT NULL                            | タスク種別（classification, regression, clustering） |
| target_column | VARCHAR(255) | NULL                                | ターゲット列名（クラスタリングの場合は NULL）        |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                                             |
| updated_at    | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新日時                                             |

**インデックス**: `user_id`, `dataset_id`（検索を高速化）

### plan_steps テーブル

前処理プランの各ステップ情報を格納するテーブル。

| カラム名     | 型           | 制約                                | 説明                                  |
| ------------ | ------------ | ----------------------------------- | ------------------------------------- |
| id           | UUID         | PRIMARY KEY                         | ステップ ID（UUID）                   |
| plan_id      | UUID         | FOREIGN KEY (plans.id), NOT NULL    | プラン ID                             |
| order        | INTEGER      | NOT NULL                            | 実行順序（1 から開始）                |
| name         | VARCHAR(255) | NOT NULL                            | ステップ名                            |
| description  | TEXT         | NULL                                | ステップの説明                        |
| code_snippet | TEXT         | NOT NULL                            | 実行するコード（pandas/scikit-learn） |
| created_at   | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                              |

**インデックス**: `plan_id`（プランごとのステップ検索を高速化）

**ユニーク制約**: `(plan_id, order)`（同じプラン内で順序は一意）

### executions テーブル

プラン実行履歴を格納するテーブル。

| カラム名            | 型          | 制約                                | 説明                                                  |
| ------------------- | ----------- | ----------------------------------- | ----------------------------------------------------- |
| id                  | UUID        | PRIMARY KEY                         | 実行 ID（UUID）                                       |
| plan_id             | UUID        | FOREIGN KEY (plans.id), NOT NULL    | プラン ID                                             |
| status              | VARCHAR(50) | NOT NULL                            | 実行ステータス（pending, running, completed, failed） |
| before_summary_json | TEXT        | NULL                                | 実行前のサマリ（JSON 形式）                           |
| after_summary_json  | TEXT        | NULL                                | 実行後のサマリ（JSON 形式）                           |
| error_message       | TEXT        | NULL                                | エラーメッセージ（失敗時）                            |
| execution_time      | FLOAT       | NULL                                | 総実行時間（秒）                                      |
| created_at          | TIMESTAMP   | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時                                              |
| completed_at        | TIMESTAMP   | NULL                                | 完了日時                                              |

**インデックス**: `plan_id`（プランごとの実行履歴検索を高速化）

### execution_step_logs テーブル

プラン実行時の各ステップのログを格納するテーブル。

| カラム名       | 型           | 制約                                  | 説明                                  |
| -------------- | ------------ | ------------------------------------- | ------------------------------------- |
| id             | UUID         | PRIMARY KEY                           | ログ ID（UUID）                       |
| execution_id   | UUID         | FOREIGN KEY (executions.id), NOT NULL | 実行 ID                               |
| step_order     | INTEGER      | NOT NULL                              | ステップの順序                        |
| step_name      | VARCHAR(255) | NOT NULL                              | ステップ名                            |
| status         | VARCHAR(50)  | NOT NULL                              | ステップステータス（success, failed） |
| execution_time | FLOAT        | NULL                                  | ステップの実行時間（秒）              |
| error_message  | TEXT         | NULL                                  | エラーメッセージ（失敗時）            |
| created_at     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TIMESTAMP   | 作成日時                              |

**インデックス**: `execution_id`（実行ごとのログ検索を高速化）

## テーブル間のリレーション

```
users (1) ──< (N) datasets
datasets (1) ──< (N) column_profiles
datasets (1) ──< (N) plans
users (1) ──< (N) plans
plans (1) ──< (N) plan_steps
plans (1) ──< (N) executions
executions (1) ──< (N) execution_step_logs
```

## Pydantic モデル（API 用）

### 認証関連

#### UserRegister

```python
class UserRegister(BaseModel):
    email: str
    password: str
```

#### UserLogin

```python
class UserLogin(BaseModel):
    email: str
    password: str
```

#### UserResponse

```python
class UserResponse(BaseModel):
    user_id: UUID
    email: str
    created_at: datetime
```

#### TokenResponse

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

### データセット関連

#### DatasetUpload

```python
class DatasetUpload(BaseModel):
    name: Optional[str] = None  # オプション、デフォルトはファイル名
```

#### DatasetSummary

```python
class DatasetSummary(BaseModel):
    dataset_id: UUID
    name: str
    rows: int
    columns: int
    created_at: datetime
```

#### DatasetDetail

```python
class DatasetDetail(BaseModel):
    dataset_id: UUID
    name: str
    rows: int
    columns: int
    file_path: str
    created_at: datetime
```

#### ColumnProfile

```python
class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_rate: float
    unique_count: int
    statistics: Dict[str, Any]  # データ型に応じた統計量
```

#### DatasetProfileResponse

```python
class DatasetProfileResponse(BaseModel):
    dataset_id: UUID
    columns: List[ColumnProfile]
```

### プラン関連

#### PlanCreate

```python
class PlanCreate(BaseModel):
    task_type: str  # "classification", "regression", "clustering"
    target_column: Optional[str] = None
    plan_name: Optional[str] = None
```

#### PlanStep

```python
class PlanStep(BaseModel):
    order: int
    name: str
    description: Optional[str] = None
    code_snippet: str
```

#### PlanResponse

```python
class PlanResponse(BaseModel):
    plan_id: UUID
    dataset_id: UUID
    task_type: str
    target_column: Optional[str]
    name: Optional[str]
    steps: List[PlanStep]
    created_at: datetime
```

### 実行関連

#### ExecutionSummary

```python
class ExecutionSummary(BaseModel):
    rows: int
    columns: int
    missing_values: int
    # その他の統計量
```

#### ExecutionStepLog

```python
class ExecutionStepLog(BaseModel):
    order: int
    name: str
    status: str  # "success", "failed"
    execution_time: Optional[float]
    error_message: Optional[str]
```

#### ExecutionResponse

```python
class ExecutionResponse(BaseModel):
    execution_id: UUID
    plan_id: UUID
    status: str  # "pending", "running", "completed", "failed"
    before: ExecutionSummary
    after: Optional[ExecutionSummary]
    steps: List[ExecutionStepLog]
    created_at: datetime
```

## データベース初期化

### SQLite 使用時

- 開発環境では SQLite を使用
- ファイルパス: `./data/cleanflow_agent.db`
- マイグレーション: Alembic を使用（将来拡張）または初期スクリプトでテーブル作成

### 本番環境想定

- PostgreSQL 等のリレーショナルデータベース
- 接続プール設定
- バックアップ戦略

## データ整合性

### 外部キー制約

- すべての外部キーに CASCADE DELETE を設定（ユーザー削除時に関連データも削除）
- または、ユーザー削除前にデータ削除を確認

### トランザクション

- データセットアップロード時: ファイル保存と DB 保存を同一トランザクションで実行
- プラン生成時: プランとステップの保存を同一トランザクションで実行
- プラン実行時: 実行履歴とログの保存を同一トランザクションで実行
