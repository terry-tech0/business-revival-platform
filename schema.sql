-- ============================================================
-- schema.sql — データベーススキーマ定義
-- ============================================================
-- 【担当者】のずちゃん（DB担当）
--
-- 【TODO（写経ポイント）】
--   1. employees テーブル  ★ CREATE TABLE 文の書き方を学ぶ
--   2. session_logs テーブル ★ JSON文字列をTEXT型で保存する設計を学ぶ
--   3. インデックス       ★ 検索高速化のための INDEX を学ぶ
--
-- 【ヒント】
--   - CREATE TABLE IF NOT EXISTS で既存テーブルがあってもエラーにならない
--   - INTEGER PRIMARY KEY AUTOINCREMENT で自動採番
--   - TEXT はカンマ区切りで複数値を保存（例: "Python,AI,財務"）
--   - REAL は小数点付き数値（スコア等）
--   - DEFAULT で初期値設定（DEFAULT 0, DEFAULT CURRENT_TIMESTAMP）
-- ============================================================


-- TODO 1: 社員テーブル（テクゼロン人財DB）
CREATE TABLE IF NOT EXISTS employees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    age             INTEGER,
    gender          TEXT,
    department      TEXT,
    position        TEXT,
    years_experience INTEGER DEFAULT 0,
    skills          TEXT,           -- カンマ区切り（例: "Python,マーケティング,財務分析"）
    mbti            TEXT,           -- 例: "ENTJ"
    has_mba         INTEGER DEFAULT 0,  -- 0=なし, 1=あり
    past_projects   TEXT,           -- 過去のプロジェクト実績（カンマ区切り）
    specialty       TEXT,           -- 専門領域
    leadership_score REAL DEFAULT 0.0,  -- リーダーシップ評価（1-5）
    creativity_score REAL DEFAULT 0.0,  -- 創造性評価（1-5）
    execution_score  REAL DEFAULT 0.0,  -- 実行力評価（1-5）
    communication_score REAL DEFAULT 0.0, -- コミュニケーション評価（1-5）
    profile_summary TEXT,           -- 一言プロフィール
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TODO 2: セッションログ（分析結果の保存用）
-- ★ リーンキャンバス結果の保存カラムを追加
CREATE TABLE IF NOT EXISTS session_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    market_input    TEXT NOT NULL,
    pest_result     TEXT,
    five_forces_result TEXT,
    selected_issue  TEXT,
    selected_solution TEXT,
    lean_canvas_result TEXT,        -- ★ 新規追加：リーンキャンバスJSON
    team_members    TEXT,           -- JSON形式で保存
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TODO 3: インデックス（検索高速化）
CREATE INDEX IF NOT EXISTS idx_employee_skills ON employees(skills);
CREATE INDEX IF NOT EXISTS idx_employee_mbti ON employees(mbti);
CREATE INDEX IF NOT EXISTS idx_employee_department ON employees(department);
