"""
services/osha_rule.py
=====================
OSHA 20%ルール正式仕様の推奨作業割合計算ロジック。
"""

import logging
from datetime import date, timedelta  # noqa: F401
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class OSHAParams:
    start_ratio: float = 0.2
    increment_ratio: float = 0.2
    max_ratio: float = 1.0
    returning_absence_min: int = 3  # 経験者リセットの欠勤閾値
    returning_absence_max: int = 7  # 新規扱いに戻す欠勤閾値

@dataclass
class WorkLog:
    date: date
    status: str  # "出" or "欠"

def recommend_ratio(
    work_history: List[WorkLog],   # 昇順（日付古→新）
    today: date,
    params: OSHAParams
) -> float:
    """
    OSHA 20%ルール正式仕様に基づき、推奨作業割合（0.2〜1.0）を返す。
    - 新規/完全非慣化: 20→40→60→80→100%
    - 経験者で3〜6連続欠勤: 50→60→80→100%
    - 7日以上欠勤: 新規扱い（20%から）
    - 1-2日欠勤: 慣化レベル維持
    - 欠勤は status="欠" で判定
    """
    if not work_history:
        logger.info("work_historyが空のため新規扱い")
        return params.start_ratio

    # 欠勤連続日数
    absence_streak = 0
    for log in reversed(work_history):
        if log.status == "欠":
            absence_streak += 1
        else:
            break

    # 欠勤明けからの連続出勤数（直近の欠勤からの連続出勤数）
    def get_logs_after_last_absence(logs):
        idx = len(logs)
        for i in range(len(logs)-1, -1, -1):
            if logs[i].status == "欠":
                idx = i
                break
        return logs[idx:]

    # 新規/完全非慣化
    if absence_streak >= params.returning_absence_max or (len(work_history) == 1 and work_history[-1].status == "出"):
        logs = get_logs_after_last_absence(work_history)
        n = len(logs)
        n = min(n, 5)
        if n == 0:
            ratio = params.start_ratio
        else:
            # Day1: 20%, Day2: 40%, ... Day5: 100%
            ratio = min(params.start_ratio + (n-1) * params.increment_ratio, params.max_ratio)
        logger.info(f"新規扱い: n={n}, ratio={ratio}")
        return round(ratio, 2)

    # 経験者で3〜6連続欠勤
    if absence_streak >= params.returning_absence_min:
        logs = get_logs_after_last_absence(work_history)
        n = len(logs)
        n = min(n, 4)
        returning_steps = [0.5, 0.6, 0.8, 1.0]
        if n == 0:
            ratio = returning_steps[0]
        else:
            ratio = returning_steps[n-1]
        logger.info(f"経験者リセット: n={n}, ratio={ratio}")
        return round(ratio, 2)

    # 1-2日欠勤 or 出勤継続→慣化維持
    logger.info("慣化維持: 100%")
    return params.max_ratio

# TODO: recommend_ratioの全分岐・境界条件テストをtests/test_osha_rule.pyで実装

def calculate_osha_ratio(*args, **kwargs):
    """旧呼び出し側を救済するための薄いラッパー"""
    return recommend_ratio(*args, **kwargs)
