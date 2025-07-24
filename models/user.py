"""
models/user.py
==============
ユーザ・作業記録・熱中症対策記録などのPydanticモデル定義。
"""

from pydantic import BaseModel, Field
from typing import Optional, List  # noqa: F401
from datetime import date

class User(BaseModel):
    """ユーザ情報"""
    id: int
    name: str

class WorkRecord(BaseModel):
    """日次作業記録"""
    user_id: int
    work_date: date
    actual_ratio: int  # 実績作業割合（例: 20, 40, 100, 0=欠席）
    recommended_ratio: int  # OSHAルールによる推奨割合

class CountermeasureRecord(BaseModel):
    """熱中症対策実施記録"""
    user_id: int
    work_date: date
    hydrated: bool = Field(default=False, description="水分補給")
    rest_taken: bool = Field(default=False, description="休憩取得")
    memo: Optional[str] = None
