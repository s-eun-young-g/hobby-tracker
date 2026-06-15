"""Pure functions over entries: streaks, personal bests, heatmap, totals.

Kept free of the web and DB layers so they are easy to test. Dates are passed in as
``YYYY-MM-DD`` strings; ``today`` is a parameter so results are deterministic.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional


def _to_date(s: str) -> date:
    return date.fromisoformat(s)


def current_streak(dates: list[str], today: date) -> int:
    """Consecutive days up to today (or yesterday) that have at least one entry."""
    days = {_to_date(d) for d in dates}
    if not days:
        return 0
    cursor = today
    if cursor not in days:
        cursor = today - timedelta(days=1)
        if cursor not in days:
            return 0
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(dates: list[str]) -> int:
    days = sorted({_to_date(d) for d in dates})
    if not days:
        return 0
    best = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    return best


def best_score(scores: list[float], better: Optional[str]) -> Optional[float]:
    vals = [s for s in scores if s is not None]
    if not vals or better is None:
        return None
    return min(vals) if better == "low" else max(vals)


def heatmap(dates: list[str], today: date, days: int = 84) -> list[tuple[str, int]]:
    """Counts per day for the last ``days`` days, oldest first."""
    counts: dict[date, int] = {}
    for d in dates:
        dt = _to_date(d)
        counts[dt] = counts.get(dt, 0) + 1
    start = today - timedelta(days=days - 1)
    out = []
    for i in range(days):
        day = start + timedelta(days=i)
        out.append((day.isoformat(), counts.get(day, 0)))
    return out
