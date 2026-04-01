"""
ai_engine.py — OpenAI API 連携モジュール
==========================================
【担当者】テリー（クローラー/AI API担当）
【役割】OpenAI API を呼び出し、PEST分析・5F分析・課題生成・解決策生成・
        リーンキャンバス・チームマッチングを行う。
        参考アプリの crawler.py に相当する「外部からデータを取得する」役割。

【TODO（写経ポイント）】
  1. _call_openai()             — ★ OpenAI API呼び出しの共通処理（try-exceptを学ぶ）
  2. run_pest_analysis()        — ★ PEST分析の実行（2行で書ける！）
  3. run_five_forces_analysis() — ★ 5F分析の実行
  4. generate_issues()          — ★ 課題10個の生成
  5. generate_solutions()       — ★ 解決策10個の生成＆スコアリング
  6. generate_lean_canvas()     — ★ 新規追加！リーンキャンバス9ブロック生成
  7. match_team()               — ★ 最適チームの選抜

【ヒント】
  - OpenAI の Python SDK: from openai import OpenAI
  - APIキーは .env ファイルに OPENAI_API_KEY=sk-xxx... と書いて管理
  - response_format={"type": "json_object"} で JSON 出力を強制
  - 各公開関数は prompts.py のテンプレートを使って _call_openai() を呼ぶだけ！
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import (
    pest_prompt,
    five_forces_prompt,
    issues_prompt,
    solutions_prompt,
    lean_canvas_prompt,
    team_matching_prompt,
)

# .env から OPENAI_API_KEY を読み込む
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 使用するモデル（gpt-4o が高精度、gpt-4o-mini がコスト安）
MODEL = "gpt-4o"


# ---------- 共通ヘルパー ---------- #
# 【写経ポイント】try-except でエラーハンドリングする方法を学ぶ
# JSON パースエラーや API エラーが起きてもアプリが落ちないようにする

def _call_openai(prompt: str, temperature: float = 0.7) -> dict:
    """
    OpenAI API を呼び出し、JSON をパースして dict で返す。
    - response_format で JSON を強制
    - パースに失敗した場合はエラー情報を返す
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは優秀なビジネスコンサルタントです。必ず有効なJSON形式のみで回答してください。JSON以外の文字は一切出力しないでください。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        raw = response.choices[0].message.content
        return json.loads(raw)

    except json.JSONDecodeError as e:
        return {"error": f"JSONパースエラー: {e}", "raw_response": raw}
    except Exception as e:
        return {"error": f"API呼び出しエラー: {e}"}


# ---------- 公開API ---------- #
# 【写経ポイント】各関数は「プロンプト生成 → API呼び出し」の2ステップだけ！


def run_pest_analysis(market: str) -> dict:
    """PEST分析を実行する。temperature=0.5（分析系は低めで安定）"""
    prompt = pest_prompt(market)
    return _call_openai(prompt, temperature=0.5)


def run_five_forces_analysis(market: str) -> dict:
    """5つの力分析を実行する。"""
    prompt = five_forces_prompt(market)
    return _call_openai(prompt, temperature=0.5)


def generate_issues(market: str, existing_issues: list[str] | None = None) -> dict:
    """課題を10個生成する。temperature=0.8（創造性高め）"""
    prompt = issues_prompt(market, existing_issues)
    return _call_openai(prompt, temperature=0.8)


def generate_solutions(
    market: str,
    issue: str,
    target: str,
    existing_solutions: list[str] | None = None,
) -> dict:
    """解決策を10個生成＆スコアリングする。"""
    prompt = solutions_prompt(market, issue, target, existing_solutions)
    return _call_openai(prompt, temperature=0.8)


def generate_lean_canvas(
    market: str,
    issue: str,
    target: str,
    solution_title: str,
    solution_desc: str,
) -> dict:
    """
    リーンキャンバス（9ブロック）を生成する。
    【写経ポイント】★ 新規追加！選択した解決策からビジネスモデルを自動設計
    """
    prompt = lean_canvas_prompt(market, issue, target, solution_title, solution_desc)
    return _call_openai(prompt, temperature=0.6)


def match_team(solution_text: str, employees_json: str) -> dict:
    """事業案に最適な4人チームを選抜する。temperature=0.4（堅実に）"""
    prompt = team_matching_prompt(solution_text, employees_json)
    return _call_openai(prompt, temperature=0.4)


# ---------- テスト用 ---------- #
if __name__ == "__main__":
    print("=== PEST分析テスト ===")
    result = run_pest_analysis("訪日外国人アニメツーリズム")
    print(json.dumps(result, ensure_ascii=False, indent=2))
