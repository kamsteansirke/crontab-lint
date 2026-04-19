"""Format next-run schedule output for CLI display."""

from datetime import datetime
from typing import List

DATE_FORMAT = "%Y-%m-%d %H:%M"


def format_next_runs(expression: str, runs: List[datetime]) -> str:
    """Format a list of upcoming run times as a readable string."""
    lines = [f"Next runs for: {expression}"]
    lines.append("-" * 40)
    for i, run in enumerate(runs, start=1):
        lines.append(f"  {i}. {run.strftime(DATE_FORMAT)}")
    return "\n".join(lines)


def format_schedule_error(expression: str, error: str) -> str:
    """Format a schedule computation error."""
    return f"Schedule error for '{expression}': {error}"


def format_schedule_block(expression: str, runs: List[datetime], error: str = "") -> str:
    """Return either formatted runs or an error message."""
    if error:
        return format_schedule_error(expression, error)
    return format_next_runs(expression, runs)
