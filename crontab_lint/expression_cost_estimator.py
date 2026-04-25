"""Estimate the computational cost of running a cron expression over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .frequency_analyzer import analyze


@dataclass
class CostEstimate:
    expression: str
    is_valid: bool
    runs_per_day: float
    runs_per_week: float
    runs_per_month: float
    cost_level: str  # "low", "medium", "high", "very_high"
    notes: list[str] = field(default_factory=list)
    error: Optional[str] = None


def _cost_level(runs_per_day: float) -> str:
    if runs_per_day >= 1440:
        return "very_high"
    if runs_per_day >= 60:
        return "high"
    if runs_per_day >= 4:
        return "medium"
    return "low"


def _build_notes(runs_per_day: float, expression: str) -> list[str]:
    notes: list[str] = []
    if runs_per_day >= 1440:
        notes.append("Runs every minute — consider whether this frequency is necessary.")
    elif runs_per_day >= 288:
        notes.append("Runs more than once every 5 minutes — high system load potential.")
    elif runs_per_day >= 60:
        notes.append("Runs at least once per hour — moderate to high load.")
    elif runs_per_day <= 1:
        notes.append("Runs once a day or less — low impact on system resources.")
    return notes


def estimate(expression: str) -> CostEstimate:
    """Return a CostEstimate for the given cron expression."""
    analysis = analyze(expression)
    if not analysis.is_valid:
        return CostEstimate(
            expression=expression,
            is_valid=False,
            runs_per_day=0.0,
            runs_per_week=0.0,
            runs_per_month=0.0,
            cost_level="low",
            error=analysis.error,
        )

    rpd = float(analysis.runs_per_day)
    rpw = rpd * 7
    rpm = rpd * 30
    level = _cost_level(rpd)
    notes = _build_notes(rpd, expression)
    return CostEstimate(
        expression=expression,
        is_valid=True,
        runs_per_day=rpd,
        runs_per_week=rpw,
        runs_per_month=rpm,
        cost_level=level,
        notes=notes,
    )
