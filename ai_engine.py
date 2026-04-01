"""
ai_engine.py — OpenAI API 連携モジュール
==========================================
【担当】クローラー（AI API）担当
【役割】OpenAI API を呼び出し、PEST分析・5F分析・課題生成・解決策生成・チームマッチングを行う。
        参考アプリの crawler.py に相当する「外部からデータを取得する」役割。

このモジュールは prompts.py のテンプレートを使って OpenAI API にリクエストを送り、
JSON形式のレスポンスをパースして返す。
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
    team_matching_prompt,
)

# .env から OPENAI_API_KEY を読み込む
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- 共通ヘルパー ---------- #

MODEL = "gpt-4o"  # 使用するモデル（gpt-4o / gpt-4o-mini に変更可能）


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


def run_pest_analysis(market: str) -> dict:
    """
    PEST分析を実行する。

    Args:
        market: 分析対象の市場（例: "訪日外国人アニメツーリズム"）

    Returns:
        dict: {summary, politics, economy, society, technology}
    """
    prompt = pest_prompt(market)
    return _call_openai(prompt, temperature=0.5)


def run_five_forces_analysis(market: str) -> dict:
    """
    5つの力分析を実行する。

    Args:
        market: 分析対象の市場

    Returns:
        dict: {summary, total_score, rivalry, new_entrants, substitutes, supplier_power, buyer_power}
    """
    prompt = five_forces_prompt(market)
    return _call_openai(prompt, temperature=0.5)


def generate_issues(market: str, existing_issues: list[str] | None = None) -> dict:
    """
    ターゲット市場に対する課題を10個生成する。

    Args:
        market: 対象市場
        existing_issues: 既に生成済みの課題リスト（重複回避用）

    Returns:
        dict: {issues: [{id, target, issue, detail}, ...]}
    """
    prompt = issues_prompt(market, existing_issues)
    return _call_openai(prompt, temperature=0.8)


def generate_solutions(
    market: str,
    issue: str,
    target: str,
    existing_solutions: list[str] | None = None,
) -> dict:
    """
    選択された課題に対する解決策（事業案）を10個生成し、スコアリングする。

    Args:
        market: 対象市場
        issue: 選択された課題
        target: 課題のターゲット
        existing_solutions: 既に生成済みの解決策リスト（重複回避用）

    Returns:
        dict: {solutions: [{id, title, description, tech_used, scoring: {...}}, ...]}
    """
    prompt = solutions_prompt(market, issue, target, existing_solutions)
    return _call_openai(prompt, temperature=0.8)


def match_team(solution_text: str, employees_json: str) -> dict:
    """
    事業案に最適な4人チームを社員DBから選抜する。

    Args:
        solution_text: 選択された解決策の説明
        employees_json: 社員リストのJSON文字列

    Returns:
        dict: {team: [{employee_id, name, role, selection_reason, strengths_for_project}, ...],
               team_synergy, team_risk}
    """
    prompt = team_matching_prompt(solution_text, employees_json)
    return _call_openai(prompt, temperature=0.4)


# ---------- テスト用 ---------- #

if __name__ == "__main__":
    # 動作確認: PEST分析のみ実行
    print("=== PEST分析テスト ===")
    result = run_pest_analysis("訪日外国人アニメツーリズム")
    print(json.dumps(result, ensure_ascii=False, indent=2))
