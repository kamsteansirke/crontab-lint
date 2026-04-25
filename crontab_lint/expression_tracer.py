"""Trace cron expression execution over a time window, listing each trigger."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import parse, ParseError
from .scheduler import next_run, ScheduleError


@dataclass
class TraceEntry:
    index: int
    trigger_time: datetime


@dataclass
class TraceResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    entries: List[TraceEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)


def trace(
    expression: str,
    start: datetime,
    end: datetime,
    max_entries: int = 100,
) -> TraceResult:
    """Return every trigger time for *expression* in [start, end)."""
    if end <= start:
        return TraceResult(
            expression=expression,
            is_valid=False,
            error="end must be after start",
        )

    try:
        parse(expression)
    except ParseError as exc:
        return TraceResult(expression=expression, is_valid=False, error=str(exc))

    entries: List[TraceEntry] = []
    current = start
    index = 1

    while index <= max_entries:
        try:
            nxt = next_run(expression, current)
        except ScheduleError as exc:
            return TraceResult(expression=expression, is_valid=False, error=str(exc))

        if nxt >= end:
            break

        entries.append(TraceEntry(index=index, trigger_time=nxt))
        index += 1
        # Advance one minute past this trigger to find the next distinct run.
        current = nxt + timedelta(minutes=1)

    return TraceResult(expression=expression, is_valid=True, error=None, entries=entries)
