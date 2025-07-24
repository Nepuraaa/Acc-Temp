"""
services/dao/worklog_dao.py
===========================
work_logsテーブルのCRUD操作。
"""

from typing import List, Optional
from sqlmodel import select
from models.schema import WorkLog
from services.db import get_session
from datetime import date

def create_worklog(user_id: int, work_date: date, status: str, work_ratio: int) -> WorkLog:
    """日次作業記録の新規作成"""
    with get_session() as session:
        log = WorkLog(user_id=user_id, date=work_date, status=status, work_ratio=work_ratio)
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

def get_worklog(log_id: int) -> Optional[WorkLog]:
    """作業記録取得（ID指定）"""
    with get_session() as session:
        return session.get(WorkLog, log_id)

def list_worklogs(user_id: Optional[int] = None, start: Optional[date] = None, end: Optional[date] = None) -> List[WorkLog]:
    """作業記録一覧（ユーザ・期間で絞り込み可）"""
    with get_session() as session:
        stmt = select(WorkLog)
        if user_id:
            stmt = stmt.where(WorkLog.user_id == user_id)
        if start:
            stmt = stmt.where(WorkLog.date >= start)
        if end:
            stmt = stmt.where(WorkLog.date <= end)
        return session.exec(stmt).all()

def update_worklog(log_id: int, status: Optional[str] = None, work_ratio: Optional[int] = None) -> Optional[WorkLog]:
    """作業記録の更新"""
    with get_session() as session:
        log = session.get(WorkLog, log_id)
        if not log:
            return None
        if status:
            log.status = status
        if work_ratio is not None:
            log.work_ratio = work_ratio
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

def delete_worklog(log_id: int) -> bool:
    """作業記録の削除"""
    with get_session() as session:
        log = session.get(WorkLog, log_id)
        if not log:
            return False
        session.delete(log)
        session.commit()
        return True
