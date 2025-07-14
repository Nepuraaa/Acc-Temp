"""
Acc-Temp ホームページ（main.py）
=================================
Streamlit 製 Web アプリ **Acc‑Temp** のランディングページです。

🔹 **機能**
    • 中央にロゴ画像を表示。
    • 下にカード型リンクを 3 枚横一列で配置。
    • ログイン／認証機能は今回は未実装。

ロゴ画像：`images/acc-temp-logo.png` をご用意ください（無ければ警告表示）。
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

# ---------------------------------------------------------------------------
# ページ設定 -----------------------------------------------------------------
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Acc-Temp ホーム",
    page_icon="🌡️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# 1. ナビゲーションに表示するページ一覧 ---------------------------------------
# ---------------------------------------------------------------------------
PAGES = [
    {"file": "pages/a.py", "label": "管理   ", "icon": "📂"},
]

# ---------------------------------------------------------------------------
# 2. CSS スニペット -----------------------------------------------------------
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .hero-img {max-width:420px; display:block; margin:auto;}
    .nav-card {text-align:center; padding:1.2rem; border-radius:0.75rem;
               transition:0.2s; border:1px solid rgba(0,0,0,0.1);
               box-shadow:0 2px 4px rgba(0,0,0,0.05);} 
    .nav-card:hover {box-shadow:0 4px 16px rgba(0,0,0,0.15);
                     transform:translateY(-2px);} 
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3. ヒーローセクション（ロゴ） ----------------------------------------------
# ---------------------------------------------------------------------------
logo_path = Path(__file__).resolve().parent.parent / "images" / "acc-temp-logo.png"
if logo_path.exists():
    st.image(str(logo_path), caption="Acc‑Temp", class_name="hero-img")
else:
    st.warning("`images/acc-temp-logo.png` が見つかりません。ダミーロゴを配置してください。")

st.markdown("## メニュー")

# ---------------------------------------------------------------------------
# 4. ナビゲーションカード -----------------------------------------------------
# ---------------------------------------------------------------------------
cols = st.columns(len(PAGES))
for col, page in zip(cols, PAGES):
    with col:
        st.markdown(
            f"""
            <div class='nav-card'>
                <h1 style='margin:0'>{page['icon']}</h1>
                <div style='margin-top:0.5rem'>{page['label']}</div>
                <div style='margin-top:0.75rem'>
                    <a href='/{page['file']}' target='_self' style='text-decoration:none'>➡️</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
