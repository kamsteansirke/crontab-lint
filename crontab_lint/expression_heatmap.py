"""Compute a 24x7 heatmap of cron expression activity."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_lint.parser import parse, ParseError
from crontab_lint.scheduler import _match_field


@dataclass
class HeatmapCell:
    hour: int
    dow: int  # 0=Monday ... 6=Sunday
    runs_per_week: int


@dataclass
class ExpressionHeatmap:
    expression: str
    is_valid: bool
    error: Optional[str]
    cells: List[HeatmapCell] = field(default_factory=list)
    peak_hour: Optional[int] = None
    peak_dow: Optional[int] = None

    def total_weekly_runs(self) -> int:
        return sum(c.runs_per_week for c in self.cells)


def build_heatmap(expression: str) -> ExpressionHeatmap:
    """Build a 24x7 heatmap for the given cron expression."""
    try:
        expr = parse(expression)
    except ParseError as exc:
        return ExpressionHeatmap(
            expression=expression,
            is_valid=False,
            error=str(exc),
        )

    cells: List[HeatmapCell] = []
    for dow in range(7):  # 0=Monday, 6=Sunday
        cron_dow = (dow + 1) % 7  # cron: 0=Sunday
        if not _match_field(expr.dow, cron_dow, 0, 6):
            continue
        for hour in range(24):
            if not _match_field(expr.hour, hour, 0, 23):
                continue
            # count matching minutes
            minutes = sum(
                1 for m in range(60)
                if _match_field(expr.minute, m, 0, 59)
            )
            if minutes > 0:
                cells.append(HeatmapCell(hour=hour, dow=dow, runs_per_week=minutes))

    peak: Optional[HeatmapCell] = max(cells, key=lambda c: c.runs_per_week, default=None)
    return ExpressionHeatmap(
        expression=expression,
        is_valid=True,
        error=None,
        cells=cells,
        peak_hour=peak.hour if peak else None,
        peak_dow=peak.dow if peak else None,
    )
