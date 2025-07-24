"""
tests/test_measure_dao.py
=========================
measure_daoのユニットテスト。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import date
from services.dao.user_dao import create_user, delete_user
from services.dao.measure_dao import create_measure, get_measure, update_measure, delete_measure, list_measures

import pytest
from sqlmodel import SQLModel
from services.db import engine

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield

def test_measure_crud():
    user = create_user("対策記録テスト", "user")
    d = date(2025, 7, 1)
    # 作成
    measure = create_measure(user.id, d, '{"hydrated": true}', "メモ")
    assert measure.id is not None
    # 取得
    fetched = get_measure(measure.id)
    assert fetched is not None
    assert fetched.memo == "メモ"
    # 更新
    updated = update_measure(measure.id, memo="更新メモ")
    assert updated.memo == "更新メモ"
    # 一覧
    measures = list_measures(user_id=user.id)
    assert any(m.id == measure.id for m in measures)
    # 削除
    assert delete_measure(measure.id) is True
    assert get_measure(measure.id) is None
    delete_user(user.id)
