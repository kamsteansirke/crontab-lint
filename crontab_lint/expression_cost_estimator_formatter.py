"""Formatting helpers for CostEstimate results."""
from __future__ import annotations

from typing import Iterable

from .expression_cost_estimator import CostEstimate

_LEVEL_ICONS = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "very_high": "🔴",
}


def format_estimate(estimate: CostEstimate, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    if not estimate.is_valid:
        return (
            f"{prefix}[INVALID] {estimate.expression}\n"
            f"  Error: {estimate.error or 'unknown error'}"
        )
    icon = _LEVEL_ICONS.get(estimate.cost_level, "")
    lines = [
        f"{prefix}{estimate.expression}",
        f"  Cost level : {icon} {estimate.cost_level.replace('_', ' ').upper()}",
        f"  Runs/day   : {estimate.runs_per_day:,.1f}",
        f"  Runs/week  : {estimate.runs_per_week:,.1f}",
        f"  Runs/month : {estimate.runs_per_month:,.1f}",
    ]
    for note in estimate.notes:
        lines.append(f"  ⚠  {note}")
    return "\n".join(lines)


def format_estimates(estimates: Iterable[CostEstimate]) -> str:
    parts = [
        format_estimate(est, index=i + 1)
        for i, est in enumerate(estimates)
    ]
    return "\n\n".join(parts) if parts else "No estimates to display."


def format_summary(estimates: list[CostEstimate]) -> str:
    valid = [e for e in estimates if e.is_valid]
    invalid = [e for e in estimates if not e.is_valid]
    if not estimates:
        return "No expressions provided."
    level_counts: dict[str, int] = {}
    for e in valid:
        level_counts[e.cost_level] = level_counts.get(e.cost_level, 0) + 1
    summary_lines = [
        f"Total      : {len(estimates)}",
        f"Valid      : {len(valid)}",
        f"Invalid    : {len(invalid)}",
    ]
    for level in ("very_high", "high", "medium", "low"):
        count = level_counts.get(level, 0)
        if count:
            icon = _LEVEL_ICONS.get(level, "")
            summary_lines.append(
                f"  {icon} {level.replace('_', ' ').capitalize():<10}: {count}"
            )
    return "\n".join(summary_lines)
