"""Format CalendarView objects for terminal output."""

from __future__ import annotations

from .expression_calendar import CalendarDay, CalendarView

_DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_BAR_CHAR = "█"
_MAX_BAR = 20


def _bar(count: int, max_count: int) -> str:
    if max_count == 0:
        return ""
    length = round(_MAX_BAR * count / max_count)
    return _BAR_CHAR * length


def format_day(day: CalendarDay, max_count: int = 1, index: Optional[int] = None) -> str:
    from typing import Optional  # noqa: F401 – inline to avoid circular issues
    weekday = _DAY_ABBR[day.date.weekday()]
    date_str = day.date.strftime("%Y-%m-%d")
    bar = _bar(day.count, max_count)
    prefix = f"{index:>3}. " if index is not None else "     "
    return f"{prefix}{weekday} {date_str}  {day.count:>4} runs  {bar}"


def format_calendar(view: CalendarView) -> str:
    lines = [f"Calendar for: {view.expression}"]
    lines.append(f"Range: {view.start.strftime('%Y-%m-%d')} + {view.days} days")
    lines.append("")

    if not view.is_valid:
        lines.append(f"  ERROR: {view.error}")
        return "\n".join(lines)

    max_count = max((d.count for d in view.calendar), default=1) or 1
    for i, day in enumerate(view.calendar, start=1):
        lines.append(format_day(day, max_count=max_count, index=i))

    lines.append("")
    lines.append(f"Total runs over {view.days} days: {view.total_runs}")
    return "\n".join(lines)


def format_summary(views: list) -> str:
    lines = ["=== Calendar Summary ==="]
    for view in views:
        status = f"{view.total_runs} runs" if view.is_valid else f"ERROR: {view.error}"
        lines.append(f"  {view.expression:<40} {status}")
    return "\n".join(lines)
