"""
models/schema.py
================
SQLModelによるテーブル定義（users, work_logs, heatstroke_measures）。
"""

from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship

# noqa: E302
class User(SQLModel, table=True):
    """ユーザ情報"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str = Field(default="")  # ハッシュ化推奨だが今回は平文可
    role: str = "user"  # "user" or "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    work_logs: list["WorkLog"] = Relationship(back_populates="user")
    measures: list["HeatstrokeMeasure"] = Relationship(back_populates="user")

class WorkLog(SQLModel, table=True):
    """日次作業記録"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    status: str  # "出", "欠" など
    work_ratio: int  # 20, 40, ... 0=欠勤

    user: Optional[User] = Relationship(back_populates="work_logs")

class HeatstrokeMeasure(SQLModel, table=True):
    """熱中症対策実施記録"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date
    measures_json: str  # JSON文字列でチェック内容を保存
    memo: Optional[str] = None

    user: Optional[User] = Relationship(back_populates="measures")
