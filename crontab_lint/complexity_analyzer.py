"""Analyze the syntactic complexity of crontab expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseError


@dataclass
class ComplexityDetail:
    category: str
    points: int
    reason: str


@dataclass
class ComplexityResult:
    expression: str
    is_valid: bool
    total: int
    level: str  # simple | moderate | complex | very_complex
    details: List[ComplexityDetail] = field(default_factory=list)
    error: str = ""


def _count_tokens(value: str) -> int:
    """Count comma-separated tokens in a field value."""
    return len(value.split(","))


def _has_step(value: str) -> bool:
    return "/" in value


def _has_range(value: str) -> bool:
    return "-" in value


def _is_wildcard(value: str) -> bool:
    return value.strip() == "*"


def _level(total: int) -> str:
    if total <= 2:
        return "simple"
    if total <= 5:
        return "moderate"
    if total <= 9:
        return "complex"
    return "very_complex"


def analyze(expression: str) -> ComplexityResult:
    """Return a ComplexityResult for *expression*."""
    try:
        cron = parse(expression)
    except ParseError as exc:
        return ComplexityResult(
            expression=expression,
            is_valid=False,
            total=0,
            level="simple",
            error=str(exc),
        )

    details: List[ComplexityDetail] = []
    fields = [
        ("minute", cron.minute),
        ("hour", cron.hour),
        ("day_of_month", cron.day_of_month),
        ("month", cron.month),
        ("day_of_week", cron.day_of_week),
    ]

    for name, value in fields:
        if _is_wildcard(value):
            continue
        tokens = _count_tokens(value)
        if tokens > 1:
            details.append(ComplexityDetail(name, tokens - 1, f"{tokens} list values"))
        if _has_range(value):
            details.append(ComplexityDetail(name, 1, "range expression"))
        if _has_step(value):
            details.append(ComplexityDetail(name, 1, "step expression"))

    total = sum(d.points for d in details)
    return ComplexityResult(
        expression=expression,
        is_valid=True,
        total=total,
        level=_level(total),
        details=details,
    )
