"""Compute next run times for cron expressions."""

from datetime import datetime, timedelta
from typing import List, Optional
from .parser import CronExpression, parse, ParseError


class ScheduleError(Exception):
    pass


def _match_field(value: int, field_str: str, min_val: int, max_val: int) -> bool:
    """Check if a value matches a cron field string."""
    if field_str == "*":
        return True
    for part in field_str.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else start)
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if value == int(part):
                return True
    return False


def next_run(expression: str, after: Optional[datetime] = None) -> datetime:
    """Return the next datetime a cron expression would fire after `after`."""
    if after is None:
        after = datetime.now()

    try:
        expr = parse(expression)
    except ParseError as e:
        raise ScheduleError(f"Cannot compute schedule: {e}") from e

    # Start one minute after `after`, truncated to the minute
    current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    for _ in range(527040):  # max 1 year of minutes
        if (
            _match_field(current.minute, expr.minute, 0, 59)
            and _match_field(current.hour, expr.hour, 0, 23)
            and _match_field(current.day, expr.day_of_month, 1, 31)
            and _match_field(current.month, expr.month, 1, 12)
            and _match_field(current.weekday() + 1, expr.day_of_week, 1, 7)
        ):
            return current
        current += timedelta(minutes=1)

    raise ScheduleError("No matching time found within one year")


def next_n_runs(expression: str, n: int = 5, after: Optional[datetime] = None) -> List[datetime]:
    """Return the next `n` datetimes a cron expression would fire."""
    results: List[datetime] = []
    current = after
    for _ in range(n):
        t = next_run(expression, after=current)
        results.append(t)
        current = t
    return results
