"""
app.py — Streamlit メインアプリケーション
==========================================
【担当】フロント担当
【役割】ユーザーインターフェースを構築する。
        「検索 → 市場分析 → 課題一覧 → 解決策 → チーム編成」のフローを管理する。
        参考アプリの app.py に相当する。

起動コマンド: streamlit run app.py
"""

import streamlit as st
import json
from database import init_db, get_all_employees, save_session_log
from ai_engine import (
    run_pest_analysis,
    run_five_forces_analysis,
    generate_issues,
    generate_solutions,
)
from matching import (
    rank_solutions,
    format_score_display,
    build_team_for_solution,
    get_mbti_compatibility_note,
    SCORING_AXES,
)

# ---------- ページ設定 ---------- #

st.set_page_config(
    page_title="人財駆動型・企業再興プラットフォーム",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# DB 初期化
init_db()

# ---------- セッション状態の初期化 ---------- #

DEFAULT_STATE = {
    "current_step": 1,       # 現在のステップ (1-5)
    "market_input": "",      # 入力された市場・ターゲット
    "pest_result": None,     # PEST分析結果
    "five_forces_result": None,  # 5F分析結果
    "issues": [],            # 生成された課題一覧（累積）
    "selected_issue": None,  # 選択された課題
    "solutions": [],         # 生成された解決策一覧（累積）
    "selected_solution": None,  # 選択された解決策
    "team_result": None,     # チーム編成結果
    "analysis_done": False,  # 市場分析完了フラグ
}

for key, default in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------- サイドバー ---------- #

with st.sidebar:
    st.markdown("## 🧭 ナビゲーション")

    steps = [
        "① 市場・ターゲット入力",
        "② 市場分析 (PEST/5F)",
        "③ 課題の探索",
        "④ 解決策の生成",
        "⑤ チーム編成",
    ]

    for i, step_name in enumerate(steps, start=1):
        if i < st.session_state.current_step:
            st.markdown(f"✅ ~~{step_name}~~")
        elif i == st.session_state.current_step:
            st.markdown(f"▶️ **{step_name}**")
        else:
            st.markdown(f"⬜ {step_name}")

    st.divider()

    if st.button("🔄 最初からやり直す", use_container_width=True):
        for key, default in DEFAULT_STATE.items():
            st.session_state[key] = default
        st.rerun()

    st.divider()
    st.caption("人財駆動型・企業再興プラットフォーム v0.1 (MVP)")


# ---------- メインヘッダー ---------- #

st.title("🚀 人財駆動型・企業再興プラットフォーム")
st.caption("市場を入力 → AI分析 → 課題発見 → 解決策生成 → 最適チーム編成")
st.divider()


# ============================================================
# STEP 1: 市場・ターゲット入力
# ============================================================

if st.session_state.current_step == 1:
    st.header("① 市場・ターゲットを入力")
    st.markdown("攻めたい市場やターゲットを自由に入力してください。")

    market = st.text_input(
        "市場・ターゲット",
        value=st.session_state.market_input,
        placeholder="例: 訪日外国人アニメツーリズム、シニア向けヘルスケア、地方創生×DX ...",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 分析開始", type="primary", use_container_width=True):
            if market.strip():
                st.session_state.market_input = market.strip()
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.warning("市場・ターゲットを入力してください。")

    # 入力例
    with st.expander("💡 入力例を見る"):
        examples = [
            "訪日外国人アニメツーリズム",
            "シニア向け健康管理×ウェアラブル",
            "中小企業の人材不足×AIマッチング",
            "地方創生×リモートワーク",
            "食品ロス削減×シェアリングエコノミー",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}"):
                st.session_state.market_input = ex
                st.session_state.current_step = 2
                st.rerun()


# ============================================================
# STEP 2: 市場分析 (PEST / 5 Forces)
# ============================================================

elif st.session_state.current_step == 2:
    st.header("② 市場分析")
    st.markdown(f"**対象市場:** {st.session_state.market_input}")

    # まだ分析していない場合
    if not st.session_state.analysis_done:
        with st.spinner("🔄 PEST分析と5つの力分析を実行中... (30秒ほどお待ちください)"):
            pest = run_pest_analysis(st.session_state.market_input)
            five_forces = run_five_forces_analysis(st.session_state.market_input)

            st.session_state.pest_result = pest
            st.session_state.five_forces_result = five_forces
            st.session_state.analysis_done = True
            st.rerun()

    # --- PEST分析の表示 ---
    pest = st.session_state.pest_result

    if pest and "error" not in pest:
        st.subheader("📊 PEST分析")
        st.markdown(f"**要約:** {pest.get('summary', '')}")

        pest_tabs = st.tabs(["🏛 Politics", "💰 Economy", "👥 Society", "🔬 Technology"])
        pest_keys = ["politics", "economy", "society", "technology"]
        pest_labels = ["政治的要因", "経済的要因", "社会的要因", "技術的要因"]

        for tab, key, label in zip(pest_tabs, pest_keys, pest_labels):
            with tab:
                data = pest.get(key, {})
                st.markdown(f"**{label}**")
                for point in data.get("points", []):
                    st.markdown(f"- {point}")
                st.info(f"💡 示唆: {data.get('insight', '')}")
    else:
        st.error(f"PEST分析でエラーが発生しました: {pest.get('error', '不明なエラー')}")

    st.divider()

    # --- 5F分析の表示 ---
    ff = st.session_state.five_forces_result

    if ff and "error" not in ff:
        st.subheader("⚔️ 5つの力分析")
        total = ff.get("total_score", 0)
        st.markdown(f"**総評:** {ff.get('summary', '')}")
        st.metric("参入しやすさ 合計スコア", f"{total} / 25")

        ff_keys = ["rivalry", "new_entrants", "substitutes", "supplier_power", "buyer_power"]
        ff_labels = ["業界内の競合", "新規参入の脅威", "代替品の脅威", "売り手の交渉力", "買い手の交渉力"]

        for key, label in zip(ff_keys, ff_labels):
            data = ff.get(key, {})
            score = data.get("score", 0)
            with st.expander(f"{label} — {'★' * score}{'☆' * (5-score)} ({score}/5)"):
                for point in data.get("points", []):
                    st.markdown(f"- {point}")
                st.info(f"💡 示唆: {data.get('insight', '')}")
                st.caption(f"スコア根拠: {data.get('score_reason', '')}")
    else:
        st.error(f"5F分析でエラーが発生しました: {ff.get('error', '不明なエラー')}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 市場を変更する"):
            st.session_state.current_step = 1
            st.session_state.analysis_done = False
            st.session_state.pest_result = None
            st.session_state.five_forces_result = None
            st.rerun()
    with col2:
        if st.button("➡️ 課題の探索へ進む", type="primary"):
            st.session_state.current_step = 3
            st.rerun()


# ============================================================
# STEP 3: 課題の探索
# ============================================================

elif st.session_state.current_step == 3:
    st.header("③ 課題の探索")
    st.markdown(f"**対象市場:** {st.session_state.market_input}")
    st.markdown("AIが市場に関する課題を10個ずつ生成します。納得できるまで何度でも再生成できます。")

    # 課題を生成するボタン
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_label = "🔍 課題を生成する" if not st.session_state.issues else "🔄 さらに10個生成"
        if st.button(generate_label, type="primary", use_container_width=True):
            existing = [iss["issue"] for iss in st.session_state.issues]
            with st.spinner("🔄 課題を生成中..."):
                result = generate_issues(st.session_state.market_input, existing or None)

            if "error" not in result:
                new_issues = result.get("issues", [])
                # IDを通番で振り直す
                start_id = len(st.session_state.issues) + 1
                for i, iss in enumerate(new_issues):
                    iss["id"] = start_id + i
                st.session_state.issues.extend(new_issues)
                st.rerun()
            else:
                st.error(f"エラー: {result['error']}")

    # 課題一覧の表示
    if st.session_state.issues:
        st.subheader(f"📋 課題一覧（{len(st.session_state.issues)}件）")

        for iss in st.session_state.issues:
            with st.container():
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(
                        f"**#{iss['id']}** | 🎯 {iss.get('target', '')} | "
                        f"📌 {iss.get('issue', '')}"
                    )
                    st.caption(iss.get("detail", ""))
                with col_b:
                    if st.button("✅ 選択", key=f"sel_issue_{iss['id']}"):
                        st.session_state.selected_issue = iss
                        st.session_state.current_step = 4
                        st.rerun()
                st.divider()
    else:
        st.info("「課題を生成する」ボタンを押して、課題を生成してください。")

    if st.button("⬅️ 市場分析に戻る"):
        st.session_state.current_step = 2
        st.rerun()


# ============================================================
# STEP 4: 解決策の生成
# ============================================================

elif st.session_state.current_step == 4:
    st.header("④ 解決策の生成")

    issue = st.session_state.selected_issue
    st.markdown(f"**対象市場:** {st.session_state.market_input}")
    st.markdown(f"**選択した課題:** {issue.get('issue', '')}")
    st.markdown(f"**ターゲット:** {issue.get('target', '')} — {issue.get('detail', '')}")
    st.divider()

    # 解決策を生成するボタン
    col1, col2 = st.columns([1, 3])
    with col1:
        gen_label = "💡 解決策を生成する" if not st.session_state.solutions else "🔄 さらに10個生成"
        if st.button(gen_label, type="primary", use_container_width=True):
            existing = [s["title"] for s in st.session_state.solutions]
            with st.spinner("🔄 解決策を生成＆スコアリング中..."):
                result = generate_solutions(
                    st.session_state.market_input,
                    issue.get("issue", ""),
                    issue.get("target", ""),
                    existing or None,
                )

            if "error" not in result:
                new_sols = result.get("solutions", [])
                start_id = len(st.session_state.solutions) + 1
                for i, s in enumerate(new_sols):
                    s["id"] = start_id + i
                st.session_state.solutions.extend(new_sols)
                st.rerun()
            else:
                st.error(f"エラー: {result['error']}")

    # 解決策一覧の表示（ランキング順）
    if st.session_state.solutions:
        ranked = rank_solutions(st.session_state.solutions)
        st.subheader(f"🏆 解決策ランキング（{len(ranked)}件）")

        for sol in ranked:
            scoring = sol.get("scoring", {})
            total = scoring.get("total", 0)

            with st.expander(
                f"**#{sol['rank']}位** | ⭐ {total}/25 | {sol.get('title', '')} | 🛠 {sol.get('tech_used', '')}",
                expanded=(sol["rank"] <= 3),
            ):
                st.markdown(sol.get("description", ""))

                # スコアリング詳細
                st.markdown("---")
                st.markdown("**📊 スコアリング詳細:**")

                score_cols = st.columns(5)
                for idx, (key, label) in enumerate(SCORING_AXES):
                    axis = scoring.get(key, {})
                    with score_cols[idx]:
                        s = axis.get("score", 0)
                        st.metric(label, f"{'★' * s}{'☆' * (5-s)}")
                        st.caption(axis.get("reason", ""))

                st.divider()

                if st.button("✅ この解決策でチーム編成へ", key=f"sel_sol_{sol['id']}"):
                    st.session_state.selected_solution = sol
                    st.session_state.current_step = 5
                    st.rerun()
    else:
        st.info("「解決策を生成する」ボタンを押してください。")

    if st.button("⬅️ 課題選択に戻る"):
        st.session_state.current_step = 3
        st.session_state.solutions = []
        st.rerun()


# ============================================================
# STEP 5: チーム編成
# ============================================================

elif st.session_state.current_step == 5:
    st.header("⑤ 最適チーム編成")

    sol = st.session_state.selected_solution
    st.markdown(f"**選択した解決策:** {sol.get('title', '')}")
    st.markdown(f"**概要:** {sol.get('description', '')}")
    st.divider()

    # チーム編成を実行
    if st.session_state.team_result is None:
        with st.spinner("🔄 最適な4人チームを選抜中..."):
            team_data = build_team_for_solution(
                sol.get("title", ""),
                sol.get("description", ""),
            )
            st.session_state.team_result = team_data
            st.rerun()

    team_data = st.session_state.team_result

    if team_data and "error" not in team_data:
        team = team_data.get("team", [])

        st.subheader("👥 プロジェクトチーム")

        # チームメンバー表示
        member_cols = st.columns(len(team)) if team else []

        for i, member in enumerate(team):
            with member_cols[i]:
                st.markdown(f"### 🧑‍💼 {member.get('name', '')}")
                st.markdown(f"**役割:** {member.get('role', '')}")
                st.info(f"📝 **選抜理由:**\n{member.get('selection_reason', '')}")
                st.success(f"💪 **強み:** {member.get('strengths_for_project', '')}")

                # DBから詳細情報を取得して表示
                emp_id = member.get("employee_id")
                if emp_id:
                    from database import get_employee_by_id
                    emp = get_employee_by_id(emp_id)
                    if emp:
                        st.caption(f"部門: {emp['department']} / {emp['position']}")
                        st.caption(f"MBTI: {emp['mbti']} | MBA: {'✅' if emp['has_mba'] else '—'}")
                        st.caption(f"スキル: {emp['skills']}")

        st.divider()

        # チームのシナジーとリスク
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🤝 チームシナジー")
            st.markdown(team_data.get("team_synergy", ""))

            # MBTI相性の補足情報
            team_mbtis = []
            for member in team:
                emp_id = member.get("employee_id")
                if emp_id:
                    from database import get_employee_by_id
                    emp = get_employee_by_id(emp_id)
                    if emp:
                        team_mbtis.append(emp.get("mbti", ""))
            if team_mbtis:
                st.caption(f"MBTI構成: {' / '.join(team_mbtis)}")
                st.caption(get_mbti_compatibility_note(team_mbtis))

        with col2:
            st.subheader("⚠️ 想定リスクと対策")
            st.markdown(team_data.get("team_risk", ""))

        st.divider()

        # セッション保存
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 この結果を保存", use_container_width=True):
                log_id = save_session_log(
                    market_input=st.session_state.market_input,
                    pest_result=st.session_state.pest_result,
                    five_forces_result=st.session_state.five_forces_result,
                    selected_issue=json.dumps(st.session_state.selected_issue, ensure_ascii=False),
                    selected_solution=json.dumps(st.session_state.selected_solution, ensure_ascii=False),
                    team_members=team_data,
                )
                st.success(f"✅ セッションを保存しました (ID: {log_id})")

        with col2:
            if st.button("🔄 別のチーム編成を試す", use_container_width=True):
                st.session_state.team_result = None
                st.rerun()

        with col3:
            if st.button("⬅️ 解決策選択に戻る", use_container_width=True):
                st.session_state.current_step = 4
                st.session_state.team_result = None
                st.rerun()
    else:
        st.error(f"チーム編成でエラーが発生しました: {team_data.get('error', '不明')}")
        if st.button("🔄 再試行"):
            st.session_state.team_result = None
            st.rerun()
