"""app/pages/02_user_detail.py
User Detail画面：月間カレンダー＋登録フォーム
"""
try:
    from app.bootstrap import ensure_project_root
except ModuleNotFoundError:
    from bootstrap import ensure_project_root
ensure_project_root()

import streamlit as st
from datetime import date, timedelta
import calendar
from services.dao.user_dao import list_users
from services.dao.worklog_dao import list_worklogs, create_worklog, update_worklog
from services.dao.measure_dao import list_measures, create_measure, update_measure
from services.settings import get_osha_params
from services.osha_rule import recommend_ratio, OSHAParams, WorkLog as OSHAWorkLog
from app.auth import require_login
import pandas as pd
import json

require_login()
st.title("User Detail（登録・推奨確認・履歴）")

users = list_users()
user_names = [u.name for u in users]
user_map = {u.name: u for u in users}
selected_name = st.selectbox("ユーザ選択", user_names)
user = user_map[selected_name]

# 月選択
today = date.today()
year = st.selectbox("年", list(range(today.year-1, today.year+2)), index=1)
month = st.selectbox("月", list(range(1, 13)), index=today.month-1)
selected_date = st.session_state.get("selected_date", today)

# データ取得
start = date(year, month, 1)
end = date(year, month, calendar.monthrange(year, month)[1])
logs = list_worklogs(user_id=user.id, start=start, end=end)
measures = list_measures(user_id=user.id, start=start, end=end)

# カレンダーUI
st.subheader(f"{year}年{month}月の作業カレンダー")
cal = calendar.monthcalendar(year, month)
dow = ["月", "火", "水", "木", "金", "土", "日"]
st.write("｜".join(dow))
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].markdown("&nbsp;")
            continue
        d = date(year, month, day)
        log = next((w for w in logs if w.date == d), None)
        actual = log.work_ratio if log and log.status == "出" else 0
        status = log.status if log else "未"
        # 色分け
        if status == "欠":
            bg = "#cccccc"
        elif status == "出":
            if actual >= 100:
                bg = "#006064"
            elif actual >= 80:
                bg = "#0097a7"
            elif actual >= 60:
                bg = "#4dd0e1"
            elif actual >= 40:
                bg = "#b2ebf2"
            elif actual >= 20:
                bg = "#e0f7fa"
            else:
                bg = "#f0f0f0"
        else:
            bg = "#f0f0f0"
        style = f"background:{bg};padding:4px;border-radius:4px"
        label = f"{day}<br><span style='font-size:10px'>{status} {actual if status=='出' else ''}</span>"
        if cols[i].button(f"{day}", key=f"day-{d}"):
            st.session_state["selected_date"] = d
        if d == selected_date:
            style += ";border:2px solid orange"
        cols[i].markdown(f"<div style='{style}'>{label}</div>", unsafe_allow_html=True)

# 選択日
selected_date = st.session_state.get("selected_date", today)
st.markdown(f"### {selected_date} の登録")

today_log = next((w for w in logs if w.date == selected_date), None)
today_measure = next((m for m in measures if m.date == selected_date), None)

with st.form("today_form"):
    status = st.selectbox("出欠", ["出", "欠"], index=0 if (today_log and today_log.status == "出") else 1)
    work_ratio = st.slider("実績作業割合（%）", 0, 100, today_log.work_ratio if today_log else 20, step=20)
    hydrated = st.checkbox("水分補給", value=bool(today_measure and json.loads(today_measure.measures_json).get("hydrated", False)))
    rest_taken = st.checkbox("休憩取得", value=bool(today_measure and json.loads(today_measure.measures_json).get("rest_taken", False)))
    memo = st.text_input("メモ", value=today_measure.memo if today_measure else "")
    submitted = st.form_submit_button("登録/更新")
    if submitted:
        # worklog
        if today_log:
            update_worklog(today_log.id, status=status, work_ratio=work_ratio)
        else:
            create_worklog(user.id, selected_date, status, work_ratio)
        # measure
        measures_json = json.dumps({"hydrated": hydrated, "rest_taken": rest_taken})
        if today_measure:
            update_measure(today_measure.id, measures_json=measures_json, memo=memo)
        else:
            create_measure(user.id, selected_date, measures_json, memo)
        st.success("登録しました。")
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
