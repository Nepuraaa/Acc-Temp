"""
tests/test_user_dao.py
======================
ユーザDAOのユニットテスト。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from services.dao.user_dao import create_user, get_user, update_user, delete_user, list_users

import pytest
from sqlmodel import SQLModel
from services.db import engine

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    # テスト後にテーブル削除したい場合はここでdrop_all

def test_user_crud():
    # 作成
    user = create_user("テストユーザ", "user")
    assert user.id is not None
    # 取得
    fetched = get_user(user.id)
    assert fetched is not None
    assert fetched.name == "テストユーザ"
    # 更新
    updated = update_user(user.id, name="更新ユーザ")
    assert updated.name == "更新ユーザ"
    # 一覧
    users = list_users()
    assert any(u.id == user.id for u in users)
    # 削除
    assert delete_user(user.id) is True
    assert get_user(user.id) is None
