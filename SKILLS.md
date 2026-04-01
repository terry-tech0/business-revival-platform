# SKILLS.md — このプロジェクトに必要なスキル一覧

## 全員共通で必要なスキル

| スキル | レベル | 学習リソース |
|-------|-------|------------|
| Python 基礎 | 変数、関数、リスト、辞書、import が分かる | [Python チュートリアル](https://docs.python.org/ja/3/tutorial/) |
| Git 基礎 | clone, add, commit, push, pull, branch | [サル先生のGit入門](https://backlog.com/ja/git-tutorial/) |
| JSON の読み書き | dict ↔ JSON の変換が分かる | [Python json モジュール](https://docs.python.org/ja/3/library/json.html) |
| コマンドライン操作 | cd, ls, pip install, python 実行 | — |
| .env の使い方 | APIキーを環境変数で管理する方法 | python-dotenv ドキュメント |

---

## 🔌 AI API担当（ai_engine.py, prompts.py）

| スキル | 何に使うか | 学習リソース |
|-------|----------|------------|
| OpenAI API の使い方 | `client.chat.completions.create()` の呼び出し | [OpenAI API Docs](https://platform.openai.com/docs/api-reference) |
| プロンプトエンジニアリング | 期待通りの出力を得るためのプロンプト設計 | [Prompt Engineering Guide](https://www.promptingguide.ai/jp) |
| JSON パース | API レスポンスを dict に変換する | `json.loads()` |
| エラーハンドリング | API 呼び出し失敗時の対処 | try/except 構文 |
| f-string (フォーマット文字列) | プロンプト内に変数を埋め込む | Python 公式ドキュメント |

### 💡 学習のコツ
- まず `prompts.py` のテンプレートを読んで「何をAIに頼んでいるか」を理解する
- OpenAI Playground で実際にプロンプトを試してみる
- `response_format={"type": "json_object"}` で JSON を強制できることを覚える

---

## 🎨 フロント担当（app.py）

| スキル | 何に使うか | 学習リソース |
|-------|----------|------------|
| Streamlit 基礎 | UI 構築（st.title, st.button, st.columns 等） | [Streamlit Docs](https://docs.streamlit.io/) |
| st.session_state | 画面遷移時のデータ保持 | [Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) |
| レイアウト | st.columns, st.expander, st.tabs の使い方 | Streamlit レイアウト API |
| コールバック | ボタン押下時の処理（st.rerun） | Streamlit Docs |
| 条件分岐 | if/elif でステップごとに表示を切り替え | Python 基礎 |

### 💡 学習のコツ
- `streamlit run app.py` で起動して、ブラウザで動作確認しながら進める
- `st.session_state` がこのアプリの心臓部。print デバッグで値を確認するとよい
- まず Step 1 だけ動かしてみて、徐々にステップを増やす

---

## 🗄️ DB担当（schema.sql, seed_data.py, database.py）

| スキル | 何に使うか | 学習リソース |
|-------|----------|------------|
| SQL 基礎 | CREATE TABLE, INSERT, SELECT, WHERE | [SQL チュートリアル](https://www.w3schools.com/sql/) |
| SQLite3 (Python) | `sqlite3.connect()`, `cursor.execute()` | [Python sqlite3](https://docs.python.org/ja/3/library/sqlite3.html) |
| テーブル設計 | 社員テーブルのカラム設計 | 正規化の基礎 |
| データ型 | TEXT, INTEGER, REAL, DATETIME | SQLite ドキュメント |
| Row Factory | `conn.row_factory = sqlite3.Row` で dict 風アクセス | Python sqlite3 ドキュメント |

### 💡 学習のコツ
- DB Browser for SQLite をインストールして、data/tech0_hr.db を GUI で確認する
- まず `seed_data.py` を実行してデータを入れてから `database.py` をテストする
- `python database.py` で直接テストして、SELECT 結果を print で確認する

---

## 📊 ランキング担当（matching.py）

| スキル | 何に使うか | 学習リソース |
|-------|----------|------------|
| sorted() / lambda | 解決策をスコア順にソートする | [Python ソート HOW TO](https://docs.python.org/ja/3/howto/sorting.html) |
| リスト内包表記 | データの加工・フィルタリング | Python チュートリアル |
| 辞書操作 | scoring データの読み取りと加工 | Python 辞書メソッド |
| MBTI の基礎知識 | チーム相性判定のロジック | [16Personalities](https://www.16personalities.com/ja) |
| json.dumps / loads | 社員データの JSON 変換 | json モジュール |

### 💡 学習のコツ
- まず `rank_solutions()` の単体テストを書いて、ソートが正しく動くか確認する
- `python matching.py` で下部のテストコードを実行して動作確認
- MBTI の E/I, T/F の違いを理解するとロジックが分かりやすくなる

---

## 参考アプリとの対応関係

```
参考アプリ (week4)         →  このアプリ
─────────────────────────────────────────
crawler.py (Web取得)       →  ai_engine.py + prompts.py (AI API取得)
database.py (SQLite管理)   →  database.py (SQLite管理)   ← ほぼ同じ構造
ranking.py (TF-IDFランク)  →  matching.py (スコアランク + チーム選抜)
app.py (Streamlit UI)      →  app.py (Streamlit UI)      ← ほぼ同じ構造
schema.sql (テーブル定義)   →  schema.sql (テーブル定義)   ← ほぼ同じ構造
```
