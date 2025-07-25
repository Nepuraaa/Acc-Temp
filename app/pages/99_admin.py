"""app/pages/99_admin.py
Admin画面：OSHAパラメータ編集＋ユーザ管理
"""
try:
    from app.bootstrap import ensure_project_root
except ModuleNotFoundError:
    from bootstrap import ensure_project_root
ensure_project_root()

import streamlit as st
from services.settings import get_osha_params, update_osha_params
from services.dao.user_dao import list_users, create_user, update_user, delete_user
from app.auth import require_login

require_login(role="admin")

st.title("Admin（OSHAパラメータ編集・ユーザ管理）")

st.header("OSHAパラメータ編集")
params = get_osha_params()
with st.form("osha_params_form"):
    start_ratio = st.number_input("初期割合", 0.0, 1.0, params.start_ratio, 0.05)
    increment_ratio = st.number_input("増分", 0.0, 1.0, params.increment_ratio, 0.05)
    max_ratio = st.number_input("上限", 0.0, 1.0, params.max_ratio, 0.05)
    returning_absence_min = st.number_input("経験者リセットの欠勤閾値", 1, 10, params.returning_absence_min)
    returning_absence_max = st.number_input("新規扱いに戻す欠勤閾値", 1, 14, params.returning_absence_max)
    submitted = st.form_submit_button("更新")
    if submitted:
        update_osha_params(
            start_ratio=start_ratio,
            increment_ratio=increment_ratio,
            max_ratio=max_ratio,
            returning_absence_min=returning_absence_min,
            returning_absence_max=returning_absence_max,
        )
        st.success("OSHAパラメータを更新しました。")
        st.rerun()

st.header("ユーザ管理")
users = list_users()
with st.expander("ユーザ一覧", expanded=True):
    for u in users:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        col1.write(f"{u.name}（{u.role}）")
        new_role = col2.selectbox("ロール", ["user", "admin"], index=0 if u.role == "user" else 1, key=f"role_{u.id}")
        new_pw = col3.text_input("パスワード", value=u.password or "", type="password", key=f"pw_{u.id}")
        if col4.button("更新", key=f"update_{u.id}"):
            update_user(u.id, role=new_role, name=u.name)
            from services.db import get_session
            with get_session() as session:
                user = session.get(type(u), u.id)
                user.password = new_pw
                session.add(user)
                session.commit()
            st.success(f"{u.name}を更新しました。")
            st.rerun()
        if col4.button("削除", key=f"delete_{u.id}"):
            delete_user(u.id)
            st.warning(f"{u.name}を削除しました。")
            st.rerun()

with st.form("add_user_form"):
    st.subheader("新規ユーザ追加")
    name = st.text_input("ユーザ名")
    password = st.text_input("パスワード", type="password")
    role = st.selectbox("ロール", ["user", "admin"])
    submitted = st.form_submit_button("追加")
    if submitted and name and password:
        create_user(name, role)
        from services.db import get_session
        users = list_users()
        user = next((u for u in users if u.name == name), None)
        if user:
            with get_session() as session:
                user_db = session.get(type(user), user.id)
                user_db.password = password
                session.add(user_db)
                session.commit()
        st.success("ユーザを追加しました。")
        st.rerun()
