"""
tests/test_worklog_dao.py
=========================
worklog_daoのユニットテスト。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import date
from services.dao.user_dao import create_user, delete_user
from services.dao.worklog_dao import create_worklog, get_worklog, update_worklog, delete_worklog, list_worklogs

import pytest
from sqlmodel import SQLModel
from services.db import engine

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield

def test_worklog_crud():
    user = create_user("作業記録テスト", "user")
    d = date(2025, 7, 1)
    # 作成
    log = create_worklog(user.id, d, "出", 40)
    assert log.id is not None
    # 取得
    fetched = get_worklog(log.id)
    assert fetched is not None
    assert fetched.work_ratio == 40
    # 更新
    updated = update_worklog(log.id, work_ratio=60)
    assert updated.work_ratio == 60
    # 一覧
    logs = list_worklogs(user_id=user.id)
    assert any(l.id == log.id for l in logs)
    # 削除
    assert delete_worklog(log.id) is True
    assert get_worklog(log.id) is None
    delete_user(user.id)
