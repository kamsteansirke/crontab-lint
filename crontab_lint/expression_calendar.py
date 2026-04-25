"""Generate a human-readable calendar view of cron expression run times."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, ParseError
from .scheduler import next_n_runs, ScheduleError


@dataclass
class CalendarDay:
    date: datetime
    run_times: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.run_times)


@dataclass
class CalendarView:
    expression: str
    start: datetime
    days: int
    calendar: List[CalendarDay] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.error is None

    @property
    def total_runs(self) -> int:
        return sum(d.count for d in self.calendar)


def build_calendar(
    expression: str,
    start: Optional[datetime] = None,
    days: int = 7,
    max_runs: int = 500,
) -> CalendarView:
    """Build a CalendarView showing runs per day over *days* days."""
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    try:
        parse(expression)
    except ParseError as exc:
        return CalendarView(expression=expression, start=start, days=days, error=str(exc))

    end = start + timedelta(days=days)

    try:
        runs = next_n_runs(expression, n=max_runs, after=start)
    except ScheduleError as exc:
        return CalendarView(expression=expression, start=start, days=days, error=str(exc))

    # Bucket runs by calendar day
    day_map: dict[str, CalendarDay] = {}
    for run in runs:
        if run >= end:
            break
        key = run.strftime("%Y-%m-%d")
        if key not in day_map:
            midnight = run.replace(hour=0, minute=0, second=0, microsecond=0)
            day_map[key] = CalendarDay(date=midnight)
        day_map[key].run_times.append(run)

    # Build ordered list for the full range
    calendar: List[CalendarDay] = []
    for i in range(days):
        day_dt = (start + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        key = day_dt.strftime("%Y-%m-%d")
        calendar.append(day_map.get(key, CalendarDay(date=day_dt)))

    return CalendarView(expression=expression, start=start, days=days, calendar=calendar)
