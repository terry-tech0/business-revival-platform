-- schema.sql
-- 人財駆動型・企業再興プラットフォーム DB設計

-- 社員テーブル（人財DB）
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

-- セッションログ（分析結果の保存用、将来拡張）
CREATE TABLE IF NOT EXISTS session_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    market_input    TEXT NOT NULL,
    pest_result     TEXT,
    five_forces_result TEXT,
    selected_issue  TEXT,
    selected_solution TEXT,
    team_members    TEXT,           -- JSON形式で保存
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_employee_skills ON employees(skills);
CREATE INDEX IF NOT EXISTS idx_employee_mbti ON employees(mbti);
CREATE INDEX IF NOT EXISTS idx_employee_department ON employees(department);
