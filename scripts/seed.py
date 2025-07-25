"""
scripts/seed.py
===============
ダミーデータ投入スクリプト。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from services.dao.user_dao import create_user
from services.dao.worklog_dao import create_worklog
from services.dao.measure_dao import create_measure
from sqlmodel import Session
from services.db import engine
from services.settings import OSHAParamsModel
from sqlalchemy import func, select

def main():
    with Session(engine) as session:
        # OSHAパラメータ初期データ投入（冪等）
        count = session.exec(select(func.count()).select_from(OSHAParamsModel)).one()
        if count == 0:
            params = OSHAParamsModel(
                id=1,
                start_ratio=0.2,
                increment_ratio=0.2,
                max_ratio=1.0,
                returning_absence_min=3,
                returning_absence_max=7,
            )
            session.add(params)
            session.commit()
    # ユーザ作成
    users = [
        create_user("田中 太郎", "user"),
        create_user("佐藤 花子", "user"),
        create_user("管理者", "admin"),
    ]
    today = date.today()
    for user in users:
        # 直近14日分のwork_logsとheatstroke_measures
        for i in range(14):
            d = today - timedelta(days=13 - i)
            status = "出" if i % 5 != 0 else "欠"
            work_ratio = 20 + (i % 5) * 20 if status == "出" else 0
            create_worklog(user.id, d, status, work_ratio)
            measures_json = '{"hydrated": true, "rest_taken": true}' if status == "出" else '{}'
            memo = "暑熱対策OK" if status == "出" else ""
            create_measure(user.id, d, measures_json, memo)
    print("✅ ダミーデータ投入完了")

if __name__ == "__main__":
    main()
