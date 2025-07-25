"""
scripts/create_tables.py
========================
DBテーブル初期化スクリプト。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import SQLModel
from services.db import engine
from models import schema
from services.settings import OSHAParamsModel

def main():
    """全テーブルをDBに作成"""
    SQLModel.metadata.create_all(engine)
    print("✅ テーブル作成完了")

if __name__ == "__main__":
    main()
