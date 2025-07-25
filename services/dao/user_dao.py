"""
services/dao/user_dao.py
========================
usersテーブルのCRUD操作。
"""

from typing import List, Optional
from sqlmodel import select
from models.schema import User
from services.db import get_session

def create_user(name: str, role: str = "user") -> User:
    """ユーザ新規作成"""
    with get_session() as session:
        user = User(name=name, role=role)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user(user_id: int) -> Optional[User]:
    """ユーザ取得（ID指定）"""
    with get_session() as session:
        return session.get(User, user_id)

def list_users() -> List[User]:
    """全ユーザ一覧"""
    with get_session() as session:
        return session.exec(select(User)).all()

def update_user(user_id: int, name: Optional[str] = None, role: Optional[str] = None) -> Optional[User]:
    """ユーザ情報更新"""
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None
        if name:
            user.name = name
        if role:
            user.role = role
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def delete_user(user_id: int) -> bool:
    """ユーザ削除"""
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return False
        session.delete(user)
        session.commit()
        return True
