# API 設計書 - CleanFlow Agent

## 基本情報

### Base URL

```
/api/v1
```

### 認証方式

- JWT（JSON Web Token）
- Authorization ヘッダに Bearer トークンを含める

```
Authorization: Bearer <access_token>
```

### 共通レスポンス形式

#### 成功レスポンス

```json
{
  "data": { ... },
  "message": "Success"
}
```

#### エラーレスポンス

```json
{
  "data": null,
  "message": "エラーメッセージ"
}
```

### HTTP ステータスコード

- `200`: 成功
- `201`: 作成成功
- `400`: バリデーションエラー / リソース重複
- `401`: 認証エラー（トークン無効・期限切れ）
- `403`: 権限エラー（リソースへのアクセス権限なし）
- `404`: リソースが見つからない
- `500`: サーバー内部エラー

## 認証関連エンドポイント

### POST /auth/register

ユーザー新規登録

#### リクエスト

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### レスポンス（201 Created）

```json
{
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "User registered successfully"
}
```

### POST /auth/login

ログイン（JSON リクエスト用）

#### リクエスト

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  },
  "message": "Login successful"
}
```

### POST /auth/token

OAuth2 トークン取得（Swagger Authorize 用）

#### リクエスト

- Content-Type: `application/x-www-form-urlencoded`

```
username=user@example.com&password=securepassword123
```

#### レスポンス（200 OK）

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### GET /auth/me

現在のユーザー情報取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Success"
}
```

## データセット関連エンドポイント

### GET /datasets

データセット一覧取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "datasets": [
      {
        "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "my_dataset",
        "description": "サンプルデータセット",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1
  },
  "message": "Success"
}
```

### POST /datasets

データセット作成

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### リクエストボディ

```json
{
  "name": "my_dataset",
  "description": "サンプルデータセット"
}
```

#### レスポンス（201 Created）

```json
{
  "data": {
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "name": "my_dataset",
    "description": "サンプルデータセット",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Dataset created successfully"
}
```

## 前処理プラン関連エンドポイント

### GET /plans

前処理プラン一覧取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "plans": [
      {
        "plan_id": "789e0123-e89b-12d3-a456-426614174002",
        "name": "my_plan",
        "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
        "task_type": "classification",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1
  },
  "message": "Success"
}
```

### POST /plans

前処理プラン作成

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### リクエストボディ

```json
{
  "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
  "task_type": "classification",
  "target_column": "target",
  "plan_name": "my_plan"
}
```

#### レスポンス（201 Created）

```json
{
  "data": {
    "plan_id": "789e0123-e89b-12d3-a456-426614174002",
    "name": "my_plan",
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "task_type": "classification",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Plan created successfully"
}
```

## プラン実行関連エンドポイント

### POST /plans/{plan_id}/execute

前処理プラン実行

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### リクエストボディ（オプション）

```json
{
  "csv_data": "col1,col2,col3\n1,2,3\n4,5,6"
}
```

※ `csv_data` を省略した場合はサンプルデータで実行

#### レスポンス（201 Created）

```json
{
  "data": {
    "execution_id": "012e3456-e89b-12d3-a456-426614174003",
    "plan_id": "789e0123-e89b-12d3-a456-426614174002",
    "status": "completed",
    "before_summary": {
      "rows": 100,
      "columns": 5,
      "missing_values": 10,
      "column_info": {
        "age": {
          "dtype": "int64",
          "missing": 0,
          "unique": 45,
          "mean": 35.5,
          "std": 12.3
        }
      }
    },
    "after_summary": {
      "rows": 100,
      "columns": 5,
      "missing_values": 0,
      "column_info": { ... }
    },
    "step_logs": [
      {
        "order": 1,
        "name": "欠損値の処理",
        "status": "success",
        "execution_time": 0.05,
        "error_message": null
      }
    ],
    "execution_time": 0.15,
    "error_message": null,
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:00:01Z"
  },
  "message": "Plan executed successfully"
}
```

### GET /plans/{plan_id}/executions

プランの実行履歴一覧取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "executions": [
      {
        "execution_id": "012e3456-e89b-12d3-a456-426614174003",
        "plan_id": "789e0123-e89b-12d3-a456-426614174002",
        "status": "completed",
        "before_summary": { ... },
        "after_summary": { ... },
        "step_logs": [ ... ],
        "execution_time": 0.15,
        "created_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:00:01Z"
      }
    ],
    "total": 1
  },
  "message": "Success"
}
```

### GET /executions/{execution_id}

実行結果詳細取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "execution_id": "012e3456-e89b-12d3-a456-426614174003",
    "plan_id": "789e0123-e89b-12d3-a456-426614174002",
    "status": "completed",
    "before_summary": { ... },
    "after_summary": { ... },
    "step_logs": [ ... ],
    "execution_time": 0.15,
    "error_message": null,
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:00:01Z"
  },
  "message": "Success"
}
```

## データプロファイリング関連エンドポイント

### POST /profiling/analyze

CSVデータのプロファイリング

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### リクエストボディ

```json
{
  "csv_data": "age,income,category,score,target\n25,50000,A,75.5,1\n30,60000,B,82.3,0\n..."
}
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "rows": 100,
    "columns": 5,
    "missing_values": 10,
    "missing_rate": 0.02,
    "numeric_columns": ["age", "income", "score"],
    "categorical_columns": ["category", "target"],
    "datetime_columns": [],
    "column_profiles": {
      "age": {
        "dtype": "int64",
        "dtype_category": "numeric",
        "count": 100,
        "missing": 0,
        "missing_rate": 0.0,
        "unique": 45,
        "unique_rate": 0.45,
        "mean": 35.5,
        "std": 12.3,
        "min": 18.0,
        "max": 80.0,
        "median": 34.0,
        "q1": 25.0,
        "q3": 45.0,
        "outliers_count": 3,
        "outliers_rate": 0.03
      },
      "category": {
        "dtype": "object",
        "dtype_category": "categorical",
        "count": 100,
        "missing": 0,
        "missing_rate": 0.0,
        "unique": 3,
        "unique_rate": 0.03,
        "top_values": {
          "A": 40,
          "B": 35,
          "C": 25
        }
      }
    },
    "quality_issues": [
      {
        "type": "moderate_missing_rate",
        "severity": "medium",
        "column": "income",
        "message": "カラム 'income' に 10.0% の欠損があります",
        "suggestion": "補完方法を検討してください"
      },
      {
        "type": "high_outliers",
        "severity": "medium",
        "column": "score",
        "message": "カラム 'score' に 15.0% の外れ値があります",
        "suggestion": "外れ値の処理を検討してください"
      }
    ]
  },
  "message": "Success"
}
```

## エラーレスポンス例

### 404 Not Found - リソースが見つからない

```json
{
  "data": null,
  "message": "Dataset not found: 456e7890-e89b-12d3-a456-426614174001"
}
```

### 403 Forbidden - アクセス権限がない

```json
{
  "data": null,
  "message": "このデータセットへのアクセス権限がありません"
}
```

### 400 Bad Request - バリデーションエラー

```json
{
  "data": null,
  "message": "パスワードは8文字以上である必要があります"
}
```

### 400 Bad Request - リソース重複

```json
{
  "data": null,
  "message": "User already exists: user@example.com"
}
```

### 401 Unauthorized - 認証エラー

```json
{
  "detail": "認証情報を検証できませんでした"
}
```
