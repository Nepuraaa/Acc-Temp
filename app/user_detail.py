"""
app/user_detail.py
==================
User Detail画面：ユーザ選択→当日登録・推奨割合・履歴表示（カレンダーUI改善）
"""

import streamlit as st
from datetime import date, timedelta
from services.dao.user_dao import list_users
from services.dao.worklog_dao import list_worklogs, create_worklog, update_worklog
from services.dao.measure_dao import list_measures, create_measure, update_measure
from services.settings import get_osha_params
from services.osha_rule import recommend_ratio, OSHAParams, WorkLog as OSHAWorkLog
from app.login import require_login
import pandas as pd
import json
import altair as alt

require_login()
st.set_page_config(page_title="User Detail", page_icon="👤", layout="wide")
st.title("User Detail（登録・推奨確認・履歴）")

users = list_users()
user_names = [u.name for u in users]
user_map = {u.name: u for u in users}
selected_name = st.selectbox("ユーザ選択", user_names)
user = user_map[selected_name]
today = date.today()
start = today - timedelta(days=13)

# 当日分のworklog/measure取得
logs = list_worklogs(user_id=user.id, start=start, end=today)
measures = list_measures(user_id=user.id, start=start, end=today)
today_log = next((w for w in logs if w.date == today), None)
today_measure = next((m for m in measures if m.date == today), None)

# OSHAパラメータ取得
params_db = get_osha_params()
params = OSHAParams(
    start_ratio=params_db.start_ratio,
    increment_ratio=params_db.increment_ratio,
    max_ratio=params_db.max_ratio,
    returning_absence_min=params_db.returning_absence_min,
    returning_absence_max=params_db.returning_absence_max,
)

# OSHA推奨割合（正式ロジック）
work_history = [
    OSHAWorkLog(date=w.date, status=w.status)
    for w in sorted(logs, key=lambda x: x.date)
]
recommended = recommend_ratio(work_history, today, params)

st.subheader("本日の登録")
with st.form("today_form"):
    status = st.selectbox("出欠", ["出", "欠"], index=0 if (today_log and today_log.status == "出") else 1)
    work_ratio = st.slider("実績作業割合（%）", 0, 100, today_log.work_ratio if today_log else 20, step=20)
    hydrated = st.checkbox("水分補給", value=bool(today_measure and json.loads(today_measure.measures_json).get("hydrated", False)))
    rest_taken = st.checkbox("休憩取得", value=bool(today_measure and json.loads(today_measure.measures_json).get("rest_taken", False)))
    memo = st.text_input("メモ", value=today_measure.memo if today_measure else "")
    st.markdown(f"**推奨作業割合（OSHA正式）: {int(recommended*100)} %**")
    submitted = st.form_submit_button("登録/更新")
    if submitted:
        # worklog
        if today_log:
            update_worklog(today_log.id, status=status, work_ratio=work_ratio)
        else:
            create_worklog(user.id, today, status, work_ratio)
        # measure
        measures_json = json.dumps({"hydrated": hydrated, "rest_taken": rest_taken})
        if today_measure:
            update_measure(today_measure.id, measures_json=measures_json, memo=memo)
        else:
            create_measure(user.id, today, measures_json, memo)
        st.success("登録しました。画面を再読み込みしてください。")

# 履歴表示（カレンダーUI）
st.subheader("直近14日分の履歴（カレンダー風）")
hist_data = []
for i in range(14):
    d = start + timedelta(days=i)
    log = next((w for w in logs if w.date == d), None)
    measure = next((m for m in measures if m.date == d), None)
    # 推奨値
    hist_work = [OSHAWorkLog(date=w.date, status=w.status) for w in sorted(logs, key=lambda x: x.date) if w.date <= d]
    rec = recommend_ratio(hist_work, d, params)
    hist_data.append({
        "日付": d.strftime("%m/%d"),
        "出欠": log.status if log else "未",
        "実績割合": log.work_ratio if log and log.status == "出" else "",
        "推奨割合": int(rec * 100),
        "水分補給": "○" if measure and json.loads(measure.measures_json).get("hydrated") else "",
        "休憩取得": "○" if measure and json.loads(measure.measures_json).get("rest_taken") else "",
        "メモ": measure.memo if measure else "",
    })
df = pd.DataFrame(hist_data)

# Altairカレンダー風ヒートマップ
df["実績割合"] = pd.to_numeric(df["実績割合"], errors="coerce")
df["推奨割合"] = pd.to_numeric(df["推奨割合"], errors="coerce")
base = alt.Chart(df).encode(
    x=alt.X("日付:O", sort=list(df["日付"])),
    y=alt.Y(" ", axis=alt.Axis(labels=False, ticks=False)),  # 1行カレンダー
)
heat = base.mark_rect().encode(
    color=alt.Color("実績割合:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(title="実績割合")),
    tooltip=["日付", "出欠", "実績割合", "推奨割合", "水分補給", "休憩取得", "メモ"]
)
line = base.mark_line(point=True, color="orange").encode(
    y=alt.Y("推奨割合:Q", axis=alt.Axis(title="推奨割合(%)"))
)
st.altair_chart(heat + line, use_container_width=True)
st.dataframe(df, use_container_width=True)
