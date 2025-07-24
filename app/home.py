# app/home.py
try:
    from app.bootstrap import ensure_project_root
except ModuleNotFoundError:
    from bootstrap import ensure_project_root
ensure_project_root()

import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html

st.set_page_config(page_title="Acc-Temp（暑熱順化くん）", page_icon="🔥", layout="wide")

root = Path(__file__).resolve().parents[1]
logo_svg = root / "images" / "our_logo.svg"
logo_png = root / "images" / "our_logo.png"

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if logo_svg.exists():
        svg = logo_svg.read_text(encoding="utf-8")
        html(
            f"""
            <div style="display:flex;justify-content:center;margin:24px 0 32px;">
              <div style="max-width:480px;width:100%;transform:translateX(-30%);">
                {svg}
              </div>
            </div>
            """,
            height=220,
        )
    elif logo_png.exists():
        st.image(str(logo_png), width=320)
    else:
        st.error(f"ロゴが見つかりませんでした: {logo_svg}")

st.title("Acc-Temp（暑熱順化くん）")
st.write("暑熱順化を 20% ルールで管理するプロトタイプです。")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📊 ダッシュボードへ"):
        st.switch_page("pages/01_dashboard.py")
with col2:
    if st.button("👤 ユーザ詳細へ"):
        st.switch_page("pages/02_user_detail.py")
with col3:
    if st.button("🛠 管理画面へ"):
        st.switch_page("pages/99_admin.py")
