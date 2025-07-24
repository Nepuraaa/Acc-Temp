"""
app/dashboard.py
================
Dashboard画面：ユーザ×日付のヒートマップ・推奨vs実績差分可視化
"""

import streamlit as st
from datetime import date, timedelta
from services.dao.user_dao import list_users
from services.dao.worklog_dao import list_worklogs
from services.osha_rule import calculate_osha_ratio
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("Dashboard（ヒートマップ・推奨vs実績差分）")

# データ取得
users = list_users()
today = date.today()
start = today - timedelta(days=13)
user_ids = [u.id for u in users]
worklogs = [w for u in users for w in list_worklogs(user_id=u.id, start=start, end=today)]

# ヒートマップ用データ
heatmap_data = []
for u in users:
    for i in range(14):
        d = start + timedelta(days=i)
        log = next((w for w in worklogs if w.user_id == u.id and w.date == d), None)
        actual = log.work_ratio if log and log.status == "出" else 0
        # OSHA推奨割合（仮：初日20%、毎日20%増、最大100%）
        recommended = calculate_osha_ratio(start, d)
        diff = actual - recommended
        heatmap_data.append({
            "ユーザ名": u.name,
            "日付": d.strftime("%m/%d"),
            "実績割合": actual,
            "推奨割合": recommended,
            "差分": diff,
        })
df = pd.DataFrame(heatmap_data)

# ヒートマップ（Altair）
st.subheader("作業割合ヒートマップ（実績）")
heatmap = alt.Chart(df).mark_rect().encode(
    x=alt.X("日付:O", sort=list(df["日付"].unique())),
    y=alt.Y("ユーザ名:O", sort=list(df["ユーザ名"].unique())),
    color=alt.Color("実績割合:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(title="実績割合")),
    tooltip=["ユーザ名", "日付", "実績割合", "推奨割合", "差分"]
).properties(width=700, height=200)
st.altair_chart(heatmap, use_container_width=True)

# 差分可視化
st.subheader("推奨割合と実績の差分（棒グラフ）")
diff_df = df.groupby("日付").agg({"差分": "mean"}).reset_index()
st.bar_chart(diff_df, x="日付", y="差分")
