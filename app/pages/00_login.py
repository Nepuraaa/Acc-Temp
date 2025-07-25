from app.bootstrap import ensure_project_root
ensure_project_root()

import streamlit as st
from app.auth import login_page

login_page()
