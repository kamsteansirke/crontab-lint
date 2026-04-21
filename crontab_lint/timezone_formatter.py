"""Format timezone check results for CLI output."""

from __future__ import annotations

from typing import List

from .timezone_checker import TimezoneCheckResult


def format_result(result: TimezoneCheckResult) -> str:
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Timezone   : {result.tz_name}")
    if result.is_valid_tz:
        lines.append(f"UTC Offset : {result.utc_offset}")
        lines.append("Status     : OK")
    else:
        lines.append("UTC Offset : N/A")
        lines.append("Status     : INVALID TIMEZONE")
    if result.has_warnings:
        lines.append("Warnings:")
        for w in result.warnings:
            lines.append(f"  [{w.code}] {w.message}")
    return "\n".join(lines)


def format_results(results: List[TimezoneCheckResult]) -> str:
    if not results:
        return "No results."
    blocks = [format_result(r) for r in results]
    return "\n\n".join(blocks)


def format_summary(results: List[TimezoneCheckResult]) -> str:
    total = len(results)
    invalid_tz = sum(1 for r in results if not r.is_valid_tz)
    with_warnings = sum(1 for r in results if r.has_warnings)
    lines = [
        f"Total checked : {total}",
        f"Invalid TZ    : {invalid_tz}",
        f"With warnings : {with_warnings}",
    ]
    return "\n".join(lines)
