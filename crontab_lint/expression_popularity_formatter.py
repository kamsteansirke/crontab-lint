"""Format popularity reports and entries for display."""
from __future__ import annotations

from typing import List

from .expression_popularity import PopularityEntry, PopularityReport


def format_entry(entry: PopularityEntry, index: Optional[int] = None) -> str:
    from typing import Optional  # noqa: F401 – used in signature above
    prefix = f"{index}. " if index is not None else ""
    last = f"  (last seen: {entry.last_seen})" if entry.last_seen else ""
    return f"{prefix}{entry.expression}  —  {entry.count} use(s){last}"


# Re-import for runtime use (forward reference workaround)
from typing import Optional  # noqa: E402


def format_entry(entry: PopularityEntry, index: Optional[int] = None) -> str:  # noqa: F811
    prefix = f"{index}. " if index is not None else ""
    last = f"  (last seen: {entry.last_seen})" if entry.last_seen else ""
    return f"{prefix}{entry.expression}  —  {entry.count} use(s){last}"


def format_report(report: PopularityReport, top_n: int = 10) -> str:
    lines: List[str] = ["Expression Popularity (Top Expressions):", ""]
    entries = report.top_n(top_n)
    if not entries:
        lines.append("  No data recorded yet.")
    else:
        for i, entry in enumerate(entries, start=1):
            lines.append(f"  {format_entry(entry, index=i)}")
    return "\n".join(lines)


def format_summary(report: PopularityReport) -> str:
    total = report.total_tracked()
    total_uses = sum(e.count for e in report.entries)
    return (
        f"Popularity summary: {total} expression(s) tracked, "
        f"{total_uses} total recorded use(s)."
    )
