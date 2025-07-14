from __future__ import annotations

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
from pathlib import Path

# ---------------------------------------------------------------------------
# ページ全体の設定 ------------------------------------------------------------
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Acc‑Temp ホーム",
    page_icon="🌡️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# 1. 資格情報と認証設定 --------------------------------------------------------
# ---------------------------------------------------------------------------
# ⚠️ 本番では必ず YAML や DB に保存したハッシュ済みパスワードを読み込んでください。
NAMES      = ["管理者ユーザー", "編集者ユーザー", "閲覧者ユーザー"]
USERNAMES  = ["admin", "editor", "viewer"]
PASSWORDS  = ["admin123", "editor123", "viewer123"]  # デモ用プレーン
HASHED_PW  = stauth.Hasher(PASSWORDS).generate()

CREDENTIALS = {
    "usernames": {
        uname: {
            "name": name,
            "password": pw_hash,
            "roles": [role],
        }
        for uname, name, pw_hash, role in zip(
            USERNAMES, NAMES, HASHED_PW, ["admin", "editor", "viewer"]
        )
    }
}

AUTH = stauth.Authenticate(
    credentials=CREDENTIALS,
    cookie_name="acc_temp_auth",
    key="acc_temp_key",
    cookie_expiry_days=7,
)

name, auth_status, username = AUTH.login("ログイン", "main")

if auth_status is False:
    st.error("ユーザー名またはパスワードが正しくありません。")
elif auth_status is None:
    st.info("ログインしてください。")
else:
    # -----------------------------------------------------------------------
    # 2. ロール別ナビゲーション ---------------------------------------------
    # -----------------------------------------------------------------------
    user_roles: list[str] = CREDENTIALS["usernames"][username]["roles"]

    PAGES = [
        {
            "file": "pages/dataset_list.py",
            "label": "データセット一覧",
            "icon": "📂",
            "roles": ["admin", "editor", "viewer"],
        },
        {
            "file": "pages/train_dataset_create.py",
            "label": "学習データセット作成",
            "icon": "🛠️",
            "roles": ["admin", "editor"],
        },
        {
            "file": "pages/eval_dataset_create.py",
            "label": "評価データセット作成",
            "icon": "🧪",
            "roles": ["admin", "editor"],
        },
    ]

    allowed_pages = [p for p in PAGES if any(r in user_roles for r in p["roles"])]

    # サイドバー -------------------------------------------------------------
    with st.sidebar:
        st.write(f"👤 **{name}**  （{', '.join(user_roles)}）")
        AUTH.logout("ログアウト", "sidebar")

    # -----------------------------------------------------------------------
    # 3. ヒーローセクション ---------------------------------------------------
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <style>
        .hero-img {max-width: 420px; display:block; margin:auto;}
        .nav-card {text-align:center; padding:1.2rem; border-radius:0.75rem;
                   transition:0.2s; border:1px solid rgba(0,0,0,0.1);
                   box-shadow:0 2px 4px rgba(0,0,0,0.05);}
        .nav-card:hover {box-shadow:0 4px 16px rgba(0,0,0,0.15);
                         transform:translateY(-2px);} 
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = Path(__file__).resolve().parent.parent / "images" / "acc-temp-logo.png"
    if logo_path.exists():
        st.image(str(logo_path), caption="Acc‑Temp", class_name="hero-img")
    else:
        st.write("⚠️ `static/acc-temp-logo.png` が見つかりません。ダミーロゴを配置してください。")

    st.markdown("## メニュー")

    # -----------------------------------------------------------------------
    # 4. ナビゲーションカード -------------------------------------------------
    # -----------------------------------------------------------------------
    cols = st.columns(len(allowed_pages))
    for col, page in zip(cols, allowed_pages):
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
