"""Formatter for ExpressionHeatmap output."""
from __future__ import annotations
from crontab_lint.expression_heatmap import ExpressionHeatmap

_DOW_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MAX_BAR = 20


def _bar(value: int, max_value: int, width: int = _MAX_BAR) -> str:
    if max_value == 0:
        return " " * width
    filled = round(value / max_value * width)
    return "█" * filled + "░" * (width - filled)


def format_heatmap(heatmap: ExpressionHeatmap) -> str:
    lines = [f"Heatmap: {heatmap.expression}"]
    if not heatmap.is_valid:
        lines.append(f"  [invalid] {heatmap.error}")
        return "\n".join(lines)

    lines.append(f"  Total weekly runs : {heatmap.total_weekly_runs()}")
    if heatmap.peak_hour is not None:
        lines.append(
            f"  Peak              : {_DOW_LABELS[heatmap.peak_dow]} "
            f"{heatmap.peak_hour:02d}:xx"
        )

    # build hour x dow grid
    grid: dict[tuple[int, int], int] = {}
    for cell in heatmap.cells:
        grid[(cell.hour, cell.dow)] = cell.runs_per_week

    max_val = max(grid.values(), default=0)
    header = "Hour  " + "  ".join(f"{d:3s}" for d in _DOW_LABELS)
    lines.append("")
    lines.append(header)
    for hour in range(24):
        row_parts = []
        for dow in range(7):
            val = grid.get((hour, dow), 0)
            row_parts.append(_bar(val, max_val, width=3))
        lines.append(f"{hour:02d}:xx  " + "  ".join(row_parts))

    return "\n".join(lines)


def format_summary(heatmaps: list) -> str:
    total = len(heatmaps)
    valid = sum(1 for h in heatmaps if h.is_valid)
    return f"Heatmap summary: {valid}/{total} valid expressions processed."
