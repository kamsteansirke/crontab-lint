"""Expression retention policy checker.

Determines whether a cron expression meets a minimum or maximum
run-frequency retention policy (e.g. "must run at least once a day",
"must not run more than once an hour").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .frequency_analyzer import analyze


@dataclass
class RetentionViolation:
    rule: str
    message: str


@dataclass
class RetentionResult:
    expression: str
    is_valid: bool
    runs_per_day: Optional[float]
    violations: List[RetentionViolation] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.is_valid and len(self.violations) == 0


def check(
    expression: str,
    min_runs_per_day: Optional[float] = None,
    max_runs_per_day: Optional[float] = None,
) -> RetentionResult:
    """Check *expression* against optional min/max runs-per-day bounds.

    Parameters
    ----------
    expression:
        A cron expression string (five fields or special string).
    min_runs_per_day:
        If given, the expression must run at least this many times per day.
    max_runs_per_day:
        If given, the expression must run at most this many times per day.

    Returns
    -------
    RetentionResult
    """
    analysis = analyze(expression)

    if not analysis.is_valid:
        return RetentionResult(
            expression=expression,
            is_valid=False,
            runs_per_day=None,
            error=f"Invalid expression: {expression}",
        )

    rpd: float = analysis.runs_per_day  # type: ignore[assignment]
    violations: List[RetentionViolation] = []

    if min_runs_per_day is not None and rpd < min_runs_per_day:
        violations.append(
            RetentionViolation(
                rule="min_runs_per_day",
                message=(
                    f"Expression runs {rpd:.2f} times/day but "
                    f"minimum is {min_runs_per_day}."
                ),
            )
        )

    if max_runs_per_day is not None and rpd > max_runs_per_day:
        violations.append(
            RetentionViolation(
                rule="max_runs_per_day",
                message=(
                    f"Expression runs {rpd:.2f} times/day but "
                    f"maximum is {max_runs_per_day}."
                ),
            )
        )

    return RetentionResult(
        expression=expression,
        is_valid=True,
        runs_per_day=rpd,
        violations=violations,
    )


def check_many(
    expressions: List[str],
    min_runs_per_day: Optional[float] = None,
    max_runs_per_day: Optional[float] = None,
) -> List[RetentionResult]:
    """Apply :func:`check` to every expression in *expressions*."""
    return [
        check(expr, min_runs_per_day=min_runs_per_day, max_runs_per_day=max_runs_per_day)
        for expr in expressions
    ]
