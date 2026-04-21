"""Validate crontab expressions against environment constraints."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError


@dataclass
class EnvConstraint:
    """A single environment constraint for cron scheduling."""
    name: str
    allowed_hours: Optional[List[int]] = None   # None means no restriction
    allowed_weekdays: Optional[List[int]] = None  # 0=Sun … 6=Sat
    max_frequency_minutes: Optional[int] = None  # minimum gap between runs


@dataclass
class EnvViolation:
    constraint_name: str
    message: str


@dataclass
class EnvValidationResult:
    expression: str
    violations: List[EnvViolation] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.violations) == 0


def _parse_field_ints(value: str, min_val: int, max_val: int) -> List[int]:
    """Expand a cron field string into a sorted list of integers."""
    if value == "*":
        return list(range(min_val, max_val + 1))
    result = set()
    for part in value.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start, end = (min_val, max_val) if base == "*" else map(int, base.split("-"))
            result.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(result)


def validate_against_env(
    expression: str,
    constraint: EnvConstraint,
) -> EnvValidationResult:
    """Check whether *expression* satisfies *constraint*."""
    result = EnvValidationResult(expression=expression)

    try:
        cron = parse(expression)
    except ParseError as exc:
        result.violations.append(
            EnvViolation(constraint.name, f"Parse error: {exc}")
        )
        return result

    if constraint.allowed_hours is not None:
        hours = _parse_field_ints(cron.hour, 0, 23)
        bad = [h for h in hours if h not in constraint.allowed_hours]
        if bad:
            allowed_str = ", ".join(map(str, constraint.allowed_hours))
            result.violations.append(EnvViolation(
                constraint.name,
                f"Runs during restricted hours {bad}; allowed: [{allowed_str}]",
            ))

    if constraint.allowed_weekdays is not None:
        days = _parse_field_ints(cron.day_of_week, 0, 6)
        bad = [d for d in days if d not in constraint.allowed_weekdays]
        if bad:
            allowed_str = ", ".join(map(str, constraint.allowed_weekdays))
            result.violations.append(EnvViolation(
                constraint.name,
                f"Runs on restricted weekdays {bad}; allowed: [{allowed_str}]",
            ))

    if constraint.max_frequency_minutes is not None:
        minutes = _parse_field_ints(cron.minute, 0, 59)
        hours = _parse_field_ints(cron.hour, 0, 23)
        runs_per_hour = len(minutes)
        if runs_per_hour > 0 and len(hours) > 0:
            gap = 60 // runs_per_hour if runs_per_hour <= 60 else 1
            if gap < constraint.max_frequency_minutes:
                result.violations.append(EnvViolation(
                    constraint.name,
                    f"Frequency gap ~{gap} min is below minimum "
                    f"{constraint.max_frequency_minutes} min",
                ))

    return result
