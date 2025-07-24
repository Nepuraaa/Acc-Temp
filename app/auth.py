import os
import streamlit as st
from dotenv import load_dotenv
from services.db import get_session
from services.dao.user_dao import list_users

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

def login_page():
    st.title("Acc-Temp ログイン")
    users = list_users()
    names = [u.name for u in users] + ["ADMIN"]
    username = st.selectbox("ユーザ名", names)
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if username == "ADMIN":
            if password == ADMIN_PASSWORD:
                st.session_state["user"] = {"name": "ADMIN", "role": "admin"}
                st.rerun()
            else:
                st.error("パスワードが違います")
        else:
            user = next((u for u in users if u.name == username), None)
            if user and user.password == password:
                st.session_state["user"] = {"name": user.name, "role": user.role, "id": user.id}
                st.rerun()
            else:
                st.error("ユーザ名またはパスワードが違います")

def require_login(role: str | None = None):
    if "user" not in st.session_state:
        st.switch_page("pages/00_login.py")
    if role and st.session_state["user"].get("role") != role:
        st.error("権限がありません")
        st.stop()
