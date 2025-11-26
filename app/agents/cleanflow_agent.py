"""CleanFlow Agent - LLM連携による前処理プラン生成"""
import json
from typing import Optional
import anthropic

from app.core.config import settings


SYSTEM_PROMPT = """あなたはデータ前処理の専門家です。
与えられたデータセットのプロファイル情報とタスクタイプに基づいて、適切な前処理ステップを生成してください。

出力は必ず以下のJSON形式で返してください:
{
  "steps": [
    {
      "order": 1,
      "name": "ステップ名",
      "description": "このステップの説明",
      "code_snippet": "# Pandasコード\\ndf = df.dropna()"
    }
  ]
}

注意事項:
- code_snippetは実行可能なPythonコード(Pandas使用)であること
- 入力データフレームは変数`df`として渡される
- 処理後のデータフレームも`df`として返すこと
- 各ステップは独立して実行可能であること
- 日本語でステップ名と説明を記述すること
"""


def _build_user_prompt(profile: dict, task_type: str, target_column: Optional[str] = None) -> str:
    """ユーザープロンプトを構築"""
    prompt = f"""以下のデータセットに対する前処理プランを生成してください。

## データセットプロファイル
{json.dumps(profile, ensure_ascii=False, indent=2)}

## タスクタイプ
{task_type}
"""
    if target_column:
        prompt += f"\n## ターゲット列\n{target_column}\n"
    
    prompt += """
## 生成する前処理ステップの例
- 欠損値の処理（削除または補完）
- 外れ値の検出と処理
- カテゴリ変数のエンコーディング
- 数値変数の正規化/標準化
- 不要な列の削除
- データ型の変換

タスクタイプとデータの特性に応じて、適切なステップを選択してください。
"""
    return prompt


def generate_plan(profile: dict, task_type: str, target_column: Optional[str] = None) -> dict:
    """LLMを使って前処理プランを生成
    
    Args:
        profile: データセットのプロファイル情報
        task_type: タスクタイプ (classification, regression, clustering)
        target_column: ターゲット列名（オプション）
    
    Returns:
        生成されたプラン（steps配列を含む辞書）
    """
    # APIキーが設定されていない場合はダミーを返す
    if not settings.ANTHROPIC_API_KEY:
        return _generate_dummy_plan(profile, task_type, target_column)
    
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    user_prompt = _build_user_prompt(profile, task_type, target_column)
    
    try:
        message = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # レスポンスからJSONを抽出
        response_text = message.content[0].text
        
        # JSONブロックを抽出（```json ... ``` 形式の場合）
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        plan = json.loads(response_text)
        return plan
        
    except json.JSONDecodeError:
        # JSONパースに失敗した場合はダミーを返す
        return _generate_dummy_plan(profile, task_type, target_column)
    except anthropic.APIError:
        # API呼び出しに失敗した場合はダミーを返す
        return _generate_dummy_plan(profile, task_type, target_column)


def _generate_dummy_plan(profile: dict, task_type: str, target_column: Optional[str] = None) -> dict:
    """ダミーの前処理プランを生成（APIキー未設定時やエラー時）"""
    steps = []
    step_order = 1
    
    # 欠損値処理
    if profile.get("missing_values", 0) > 0:
        steps.append({
            "order": step_order,
            "name": "欠損値の処理",
            "description": "欠損値を含む行を削除します",
            "code_snippet": "# 欠損値を含む行を削除\ndf = df.dropna()"
        })
        step_order += 1
    
    # 数値列の標準化
    numeric_cols = profile.get("numeric_columns", [])
    if numeric_cols and task_type in ["classification", "regression"]:
        cols_str = str(numeric_cols)
        steps.append({
            "order": step_order,
            "name": "数値列の標準化",
            "description": "数値列を標準化（平均0、標準偏差1）します",
            "code_snippet": f"# 数値列の標準化\nfrom sklearn.preprocessing import StandardScaler\nnumeric_cols = {cols_str}\nscaler = StandardScaler()\ndf[numeric_cols] = scaler.fit_transform(df[numeric_cols])"
        })
        step_order += 1
    
    # カテゴリ列のエンコーディング
    categorical_cols = profile.get("categorical_columns", [])
    if categorical_cols:
        cols_str = str(categorical_cols)
        steps.append({
            "order": step_order,
            "name": "カテゴリ変数のエンコーディング",
            "description": "カテゴリ変数をラベルエンコーディングします",
            "code_snippet": f"# カテゴリ変数のラベルエンコーディング\nfrom sklearn.preprocessing import LabelEncoder\ncategorical_cols = {cols_str}\nfor col in categorical_cols:\n    le = LabelEncoder()\n    df[col] = le.fit_transform(df[col].astype(str))"
        })
        step_order += 1
    
    # ステップがない場合はデフォルトを追加
    if not steps:
        steps.append({
            "order": 1,
            "name": "データ確認",
            "description": "データの基本情報を確認します",
            "code_snippet": "# データの基本情報を表示\nprint(df.info())\nprint(df.describe())"
        })
    
    return {"steps": steps}
