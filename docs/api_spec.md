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
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ"
  }
}
```

### HTTP ステータスコード

- `200`: 成功
- `201`: 作成成功
- `400`: バリデーションエラー
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

#### エラーレスポンス例

**400 Bad Request - メール重複**

```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "このメールアドレスは既に登録されています"
  }
}
```

**400 Bad Request - パスワード強度不足**

```json
{
  "error": {
    "code": "WEAK_PASSWORD",
    "message": "パスワードは8文字以上である必要があります"
  }
}
```

### POST /auth/login

ログイン（JWT トークン取得）

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

#### エラーレスポンス例

**401 Unauthorized - 認証失敗**

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "メールアドレスまたはパスワードが正しくありません"
  }
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

#### エラーレスポンス例

**401 Unauthorized - トークン無効**

```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "トークンが無効または期限切れです"
  }
}
```

## データセット関連エンドポイント

### POST /datasets

CSV ファイルアップロード

#### リクエスト

- Content-Type: `multipart/form-data`
- 認証: 必須

```
file: <CSVファイル>
name: "my_dataset" (オプション、デフォルトはファイル名)
```

#### レスポンス（201 Created）

```json
{
  "data": {
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "name": "my_dataset",
    "rows": 1000,
    "columns": 10,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Dataset uploaded successfully"
}
```

#### エラーレスポンス例

**400 Bad Request - ファイル形式エラー**

```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "CSVファイルのみアップロード可能です"
  }
}
```

**400 Bad Request - ファイルサイズ超過**

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "ファイルサイズは100MB以下である必要があります"
  }
}
```

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
        "rows": 1000,
        "columns": 10,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1
  },
  "message": "Success"
}
```

### GET /datasets/{dataset_id}

データセット詳細取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "name": "my_dataset",
    "rows": 1000,
    "columns": 10,
    "file_path": "/data/datasets/456e7890-e89b-12d3-a456-426614174001.csv",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Success"
}
```

#### エラーレスポンス例

**404 Not Found**

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "データセットが見つかりません"
  }
}
```

**403 Forbidden**

```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "このデータセットへのアクセス権限がありません"
  }
}
```

### GET /datasets/{dataset_id}/profile

データプロファイル取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "columns": [
      {
        "name": "age",
        "dtype": "int64",
        "missing_count": 5,
        "missing_rate": 0.005,
        "unique_count": 45,
        "statistics": {
          "mean": 35.5,
          "median": 34.0,
          "std": 12.3,
          "min": 18,
          "max": 80
        }
      },
      {
        "name": "category",
        "dtype": "object",
        "missing_count": 0,
        "missing_rate": 0.0,
        "unique_count": 3,
        "statistics": {
          "value_counts": {
            "A": 400,
            "B": 350,
            "C": 250
          }
        }
      }
    ]
  },
  "message": "Success"
}
```

### DELETE /datasets/{dataset_id}

データセット削除

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001"
  },
  "message": "Dataset deleted successfully"
}
```

## 前処理プラン関連エンドポイント

### POST /datasets/{dataset_id}/plan

前処理プラン生成

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### リクエストボディ

```json
{
  "task_type": "classification",
  "target_column": "target",
  "plan_name": "my_plan" (オプション)
}
```

#### レスポンス（201 Created）

```json
{
  "data": {
    "plan_id": "789e0123-e89b-12d3-a456-426614174002",
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "task_type": "classification",
    "target_column": "target",
    "name": "my_plan",
    "steps": [
      {
        "order": 1,
        "name": "欠損値補完（数値列）",
        "description": "数値列の欠損値を平均値で補完",
        "code_snippet": "df['age'].fillna(df['age'].mean(), inplace=True)"
      },
      {
        "order": 2,
        "name": "カテゴリ変数エンコード",
        "description": "カテゴリ変数をOne-Hot Encoding",
        "code_snippet": "df = pd.get_dummies(df, columns=['category'])"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Plan generated successfully"
}
```

#### エラーレスポンス例

**400 Bad Request - 無効なタスク種別**

```json
{
  "error": {
    "code": "INVALID_TASK_TYPE",
    "message": "タスク種別は classification, regression, clustering のいずれかである必要があります"
  }
}
```

**400 Bad Request - ターゲット列が見つからない**

```json
{
  "error": {
    "code": "TARGET_COLUMN_NOT_FOUND",
    "message": "指定されたターゲット列がデータセットに存在しません"
  }
}
```

**500 Internal Server Error - LLM 生成失敗**

```json
{
  "error": {
    "code": "PLAN_GENERATION_FAILED",
    "message": "前処理プランの生成に失敗しました"
  }
}
```

### GET /plans/{plan_id}

前処理プラン詳細取得

#### リクエストヘッダ

```
Authorization: Bearer <access_token>
```

#### レスポンス（200 OK）

```json
{
  "data": {
    "plan_id": "789e0123-e89b-12d3-a456-426614174002",
    "dataset_id": "456e7890-e89b-12d3-a456-426614174001",
    "task_type": "classification",
    "target_column": "target",
    "name": "my_plan",
    "steps": [
      {
        "order": 1,
        "name": "欠損値補完（数値列）",
        "description": "数値列の欠損値を平均値で補完",
        "code_snippet": "df['age'].fillna(df['age'].mean(), inplace=True)"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Success"
}
```

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

### POST /plans/{plan_id}/execute

前処理プラン実行

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
    "before": {
      "rows": 1000,
      "columns": 10,
      "missing_values": 50
    },
    "after": {
      "rows": 1000,
      "columns": 12,
      "missing_values": 0
    },
    "steps": [
      {
        "order": 1,
        "name": "欠損値補完（数値列）",
        "status": "success",
        "execution_time": 0.05
      },
      {
        "order": 2,
        "name": "カテゴリ変数エンコード",
        "status": "success",
        "execution_time": 0.12
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Execution completed successfully"
}
```

#### エラーレスポンス例

**400 Bad Request - 実行エラー**

```json
{
  "error": {
    "code": "EXECUTION_FAILED",
    "message": "プランの実行中にエラーが発生しました",
    "details": {
      "step_order": 2,
      "error_message": "KeyError: 'category'"
    }
  }
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
    "before": { ... },
    "after": { ... },
    "steps": [ ... ],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Success"
}
```
