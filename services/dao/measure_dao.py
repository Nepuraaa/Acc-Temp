"""
services/dao/measure_dao.py
===========================
heatstroke_measuresテーブルのCRUD操作。
"""

from typing import List, Optional
from sqlmodel import select
from models.schema import HeatstrokeMeasure
from services.db import get_session
from datetime import date

def create_measure(user_id: int, measure_date: date, measures_json: str, memo: Optional[str] = None) -> HeatstrokeMeasure:
    """熱中症対策記録の新規作成"""
    with get_session() as session:
        measure = HeatstrokeMeasure(user_id=user_id, date=measure_date, measures_json=measures_json, memo=memo)
        session.add(measure)
        session.commit()
        session.refresh(measure)
        return measure

def get_measure(measure_id: int) -> Optional[HeatstrokeMeasure]:
    """記録取得（ID指定）"""
    with get_session() as session:
        return session.get(HeatstrokeMeasure, measure_id)

def list_measures(user_id: Optional[int] = None, start: Optional[date] = None, end: Optional[date] = None) -> List[HeatstrokeMeasure]:
    """記録一覧（ユーザ・期間で絞り込み可）"""
    with get_session() as session:
        stmt = select(HeatstrokeMeasure)
        if user_id:
            stmt = stmt.where(HeatstrokeMeasure.user_id == user_id)
        if start:
            stmt = stmt.where(HeatstrokeMeasure.date >= start)
        if end:
            stmt = stmt.where(HeatstrokeMeasure.date <= end)
        return session.exec(stmt).all()

def update_measure(measure_id: int, measures_json: Optional[str] = None, memo: Optional[str] = None) -> Optional[HeatstrokeMeasure]:
    """記録の更新"""
    with get_session() as session:
        measure = session.get(HeatstrokeMeasure, measure_id)
        if not measure:
            return None
        if measures_json:
            measure.measures_json = measures_json
        if memo is not None:
            measure.memo = memo
        session.add(measure)
        session.commit()
        session.refresh(measure)
        return measure

def delete_measure(measure_id: int) -> bool:
    """記録の削除"""
    with get_session() as session:
        measure = session.get(HeatstrokeMeasure, measure_id)
        if not measure:
            return False
        session.delete(measure)
        session.commit()
        return True
