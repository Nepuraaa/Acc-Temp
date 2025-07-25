"""
services/db.py
==============
DBエンジン・Session管理（.envからDB URL取得）。
"""

import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("ACC_TEMP_DB", "sqlite:///data/acc_temp.db")
engine = create_engine(DB_URL, echo=False)

def get_session():
    """DBセッション生成（with文で利用推奨）"""
    return Session(engine)
