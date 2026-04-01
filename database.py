"""
database.py — SQLite データベース操作モジュール
================================================
【担当者】のずちゃん（DB担当）
【役割】SQLiteへの接続管理、社員データの取得、セッションログの保存を行う。
        他のモジュール（app.py, matching.py）から呼び出される「データの窓口」。

【TODO（写経ポイント）】
  1. get_connection()          ★ DB接続とrow_factory設定を学ぶ
  2. init_db()                 ★ テーブル初期化 & 自動seed を学ぶ
  3. get_all_employees()       ★ SELECT * の基本を学ぶ
  4. get_employee_by_id()      ★ WHERE句とパラメータバインディングを学ぶ
  5. get_employees_by_ids()    ★ IN句の動的生成を学ぶ
  6. search_employees_by_skill() ★ LIKE句による部分一致検索を学ぶ
  7. save_session_log()        ★ INSERT + json.dumps を学ぶ（リーンキャンバス対応）

【ヒント】
  - sqlite3 は Python 標準ライブラリ（pip install 不要）
  - conn.row_factory = sqlite3.Row で結果を dict 風に扱える
  - SQL の ? はプレースホルダー（SQLインジェクション対策として必須）
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/tech0_hr.db")


# ---------- 接続管理 ---------- #

def get_connection() -> sqlite3.Connection:
    """
    SQLite データベースへの接続を返す。
    ★ row_factory を設定すると row["name"] のように辞書風にアクセスできて便利！
    """
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    schema.sql を実行してテーブルを初期化する。
    ★ 社員データが0件なら seed_data.py を自動実行する（初回起動時のみ）
    """
    conn = get_connection()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # 社員データが空なら自動投入
    cursor = conn.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        from seed_data import seed
        seed()


# ---------- 社員データ取得 ---------- #

def get_all_employees() -> list[dict]:
    """
    全社員データを取得して dict のリストで返す。
    ★ [dict(row) for row in rows] で sqlite3.Row → dict に変換
    """
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM employees ORDER BY id")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_employee_by_id(employee_id: int) -> dict | None:
    """
    社員IDで1名分のデータを取得する。
    ★ パラメータは (employee_id,) とタプルで渡す（カンマ忘れに注意！）
    """
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_employees_by_ids(ids: list[int]) -> list[dict]:
    """
    複数の社員IDでデータを取得する。
    ★ IN句の ? を動的に生成する方法を学ぶ
    """
    if not ids:
        return []
    placeholders = ",".join("?" * len(ids))
    conn = get_connection()
    cursor = conn.execute(
        f"SELECT * FROM employees WHERE id IN ({placeholders})", ids
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def search_employees_by_skill(skill: str) -> list[dict]:
    """
    スキルで社員を部分一致検索する。
    ★ LIKE '%Python%' のように前後に % をつけて部分一致
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM employees WHERE skills LIKE ?", (f"%{skill}%",)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# ---------- セッションログ ---------- #

def save_session_log(
    market_input: str,
    pest_result: dict | None = None,
    five_forces_result: dict | None = None,
    selected_issue: str | None = None,
    selected_solution: str | None = None,
    lean_canvas_result: dict | None = None,
    team_members: list | None = None,
) -> int:
    """
    1回のセッション結果をログとして保存する。
    ★ dict/list は json.dumps() で文字列に変換してから保存
    ★ リーンキャンバス結果(lean_canvas_result)の保存に対応

    Returns:
        int: 挿入されたログのID
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO session_logs
            (market_input, pest_result, five_forces_result,
             selected_issue, selected_solution, lean_canvas_result, team_members)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            market_input,
            json.dumps(pest_result, ensure_ascii=False) if pest_result else None,
            json.dumps(five_forces_result, ensure_ascii=False) if five_forces_result else None,
            selected_issue,
            selected_solution,
            json.dumps(lean_canvas_result, ensure_ascii=False) if lean_canvas_result else None,
            json.dumps(team_members, ensure_ascii=False) if team_members else None,
        ),
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


# ---------- テスト用 ---------- #

if __name__ == "__main__":
    init_db()
    employees = get_all_employees()
    print(f"テクゼロン社員数: {len(employees)}")
    for emp in employees[:3]:
        print(f"  {emp['name']} ({emp['department']}) - MBTI: {emp['mbti']}")
