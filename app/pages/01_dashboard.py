"""
app/pages/01_dashboard.py
Dashboard画面：KPI＋カレンダー/ヒートマップ風可視化＋横向きサマリ表＋可読性向上
"""
try:
    from app.bootstrap import ensure_project_root
except ModuleNotFoundError:
    from bootstrap import ensure_project_root
ensure_project_root()

import streamlit as st
from datetime import date, timedelta
from services.dao.user_dao import list_users
from services.dao.worklog_dao import list_worklogs
from services.osha_rule import WorkLog as OSHAWorkLog
import pandas as pd
import altair as alt

# --- フィルタ ---
users = list_users()
user_names = [u.name for u in users]
user_map = {u.name: u for u in users}
selected_names = st.multiselect("ユーザ選択", user_names, default=user_names)
selected_users = [user_map[n] for n in selected_names]
today = date.today()
period_days = st.slider("表示日数", 7, 31, 14)
start = today - timedelta(days=period_days - 1)

# --- データ取得 ---
user_ids = [u.id for u in selected_users]
worklogs = [w for u in selected_users for w in list_worklogs(user_id=u.id, start=start, end=today)]

# --- KPI ---
num_users = len(selected_users)
today_logs = [w for w in worklogs if w.date == today]
num_present = sum(1 for w in today_logs if w.status == "出")
num_absent = sum(1 for w in today_logs if w.status == "欠")
recent_logs = [w for w in worklogs if w.status == "出"]
avg_ratio = round(sum(w.work_ratio for w in recent_logs) / len(recent_logs), 1) if recent_logs else 0

col1, col2, col3 = st.columns(3)
col1.metric("登録ユーザ数", num_users)
col2.metric("本日の出勤者数", num_present)
col3.metric("本日の欠勤者数", num_absent)
st.metric("直近{}日の平均作業割合".format(period_days), f"{avg_ratio:.1f} %")

# --- カレンダー/ヒートマップ風可視化 ---
st.subheader("直近{}日分のユーザ×日付カレンダー".format(period_days))
show_numbers = st.checkbox("セルに数値（%/欠）を表示", value=(num_users <= 5))

dates = [start + timedelta(days=i) for i in range(period_days)]
heatmap_data = []
for u in selected_users:
    user_logs = [w for w in worklogs if w.user_id == u.id]
    for d in dates:
        log = next((w for w in user_logs if w.date == d), None)
        actual = log.work_ratio if log and log.status == "出" else 0
        status = log.status if log else "未"
        label = "欠" if status == "欠" else (f"{actual}%" if status == "出" and actual > 0 else "")
        heatmap_data.append({
            "ユーザ名": u.name,
            "日付": d.strftime("%m/%d"),
            "date": d,
            "実績割合": actual,
            "出欠": status,
            "label": label,
        })
df = pd.DataFrame(heatmap_data)

# --- 可読性向上: 高さ・フォントサイズ自動調整 ---
n_users = len(selected_users)
row_h = 50
chart_h = max(250, row_h * n_users)
font_sz = min(14, max(8, 18 - 0.5 * n_users))

color_scale = alt.Scale(
    domain=[0, 20, 40, 60, 80, 100],
    range=["#cccccc", "#e0f7fa", "#b2ebf2", "#4dd0e1", "#0097a7", "#006064"]
)
base = alt.Chart(df).encode(
    x=alt.X("日付:O", sort=list(df["日付"].unique()), axis=alt.Axis(labelAngle=-45, labelOverlap=True)),
    y=alt.Y("ユーザ名:O", sort=list(df["ユーザ名"].unique()), axis=alt.Axis(title=None), scale=alt.Scale(paddingInner=0.2, paddingOuter=0.1))
).properties(width=700, height=chart_h)

heat = base.mark_rect().encode(
    color=alt.Color("実績割合:Q", scale=color_scale, legend=alt.Legend(title="実績割合")),
    tooltip=[
        alt.Tooltip("ユーザ名:N", title="ユーザ"),
        alt.Tooltip("date:T", title="日付"),
        alt.Tooltip("実績割合:Q", title="実績割合", format=".0f"),
        alt.Tooltip("出欠:N", title="出欠")
    ]
)

if show_numbers:
    text = base.mark_text(size=font_sz).encode(
        text=alt.Text("label:N")
    )
    chart = heat + text
else:
    chart = heat

with st.container():
    st.altair_chart(chart, use_container_width=True)

# --- 横向きサマリ表 ---
st.subheader("ユーザ別サマリ（横向きKPI一覧）")
def build_summary(df):
    g = df.groupby("ユーザ名")
    summary = pd.DataFrame({
        "対象期間日数": g.size(),
        "出勤日数": g.apply(lambda s: (s["出欠"] == "出").sum()),
        "欠勤日数": g.apply(lambda s: (s["出欠"] == "欠").sum()),
        "平均実績割合(%)": g["実績割合"].mean(),
        "最大実績割合(%)": g["実績割合"].max(),
        "最小実績割合(%)": g["実績割合"].min(),
        "最新登録日": g["date"].max(),
    }).reset_index()
    summary["平均実績割合(%)"] = summary["平均実績割合(%)"].round(1)
    summary["最大実績割合(%)"] = summary["最大実績割合(%)"].round(1)
    summary["最小実績割合(%)"] = summary["最小実績割合(%)"].round(1)
    return summary

summary_df = build_summary(df)
st.dataframe(summary_df.style.format({
    "平均実績割合(%)": "{:.1f}",
    "最大実績割合(%)": "{:.1f}",
    "最小実績割合(%)": "{:.1f}",
}), use_container_width=True)
csv = summary_df.to_csv(index=False, encoding="utf-8-sig")
st.download_button("CSVダウンロード", csv, file_name="dashboard_summary.csv", mime="text/csv")
