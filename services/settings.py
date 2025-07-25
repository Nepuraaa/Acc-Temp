"""
services/settings.py
====================
OSHAパラメータのCRUD（DB保存・取得・更新）。
"""

from sqlmodel import SQLModel, Field, select  # noqa: F401
from typing import Optional
from services.db import get_session

class OSHAParamsModel(SQLModel, table=True):
    __tablename__ = "osha_params"
    id: Optional[int] = Field(default=1, primary_key=True)
    start_ratio: float = 0.2
    increment_ratio: float = 0.2
    max_ratio: float = 1.0
    returning_absence_min: int = 3
    returning_absence_max: int = 7

def get_osha_params() -> OSHAParamsModel:
    """OSHAパラメータを取得（なければデフォルトで作成）"""
    with get_session() as session:
        params = session.get(OSHAParamsModel, 1)
        if not params:
            params = OSHAParamsModel()
            session.add(params)
            session.commit()
            session.refresh(params)
        return params

def update_osha_params(**kwargs) -> OSHAParamsModel:
    """OSHAパラメータを更新"""
    with get_session() as session:
        params = session.get(OSHAParamsModel, 1)
        if not params:
            params = OSHAParamsModel()
        for k, v in kwargs.items():
            if hasattr(params, k):
                setattr(params, k, v)
        session.add(params)
        session.commit()
        session.refresh(params)
        return params
