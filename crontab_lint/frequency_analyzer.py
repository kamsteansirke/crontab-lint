"""Analyze and categorize the run frequency of cron expressions."""

from dataclasses import dataclass
from typing import Optional

from crontab_lint.parser import parse, ParseError
from crontab_lint.conflict_detector import _parse_field_values


@dataclass
class FrequencyAnalysis:
    expression: str
    is_valid: bool
    estimated_runs_per_day: Optional[float]
    category: Optional[str]  # 'high', 'medium', 'low', 'rare'
    description: Optional[str]
    error: Optional[str] = None


_CATEGORY_THRESHOLDS = [
    (1440, "high",   "more than once per minute"),
    (288,  "high",   "very frequent (every few minutes)"),
    (48,   "high",   "frequent (multiple times per hour)"),
    (24,   "medium", "roughly once per hour"),
    (4,    "medium", "several times per day"),
    (1,    "low",    "roughly once per day"),
    (0.15, "low",    "a few times per week"),
    (0,    "rare",   "once per week or less"),
]


def _count_values(field_str: str, min_val: int, max_val: int) -> int:
    """Return the number of distinct values a field matches."""
    values = _parse_field_values(field_str, min_val, max_val)
    return len(values) if values else 1


def analyze(expression: str) -> FrequencyAnalysis:
    """Return a FrequencyAnalysis for the given cron expression string."""
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return FrequencyAnalysis(
            expression=expression,
            is_valid=False,
            estimated_runs_per_day=None,
            category=None,
            description=None,
            error=str(exc),
        )

    # Special strings map to known frequencies
    special_map = {
        "@yearly":   1 / 365,
        "@annually": 1 / 365,
        "@monthly":  1 / 30,
        "@weekly":   1 / 7,
        "@daily":    1.0,
        "@midnight": 1.0,
        "@hourly":   24.0,
        "@reboot":   None,
    }
    if parsed.special:
        token = parsed.special.lower()
        rpd = special_map.get(token)
        if token == "@reboot":
            return FrequencyAnalysis(
                expression=expression,
                is_valid=True,
                estimated_runs_per_day=None,
                category="rare",
                description="once at system reboot",
            )
        category, desc = _categorize(rpd)
        return FrequencyAnalysis(
            expression=expression,
            is_valid=True,
            estimated_runs_per_day=rpd,
            category=category,
            description=desc,
        )

    minutes    = _count_values(parsed.minute,      0, 59)
    hours      = _count_values(parsed.hour,        0, 23)
    dom_vals   = _count_values(parsed.day_of_month, 1, 31)
    months     = _count_values(parsed.month,        1, 12)
    dow_vals   = _count_values(parsed.day_of_week,  0, 6)

    # Approximate days per month the job runs
    active_days_per_month = min(dom_vals, 31) * (dow_vals / 7)
    active_days_per_year  = active_days_per_month * months
    runs_per_active_day   = hours * minutes
    rpd = (active_days_per_year * runs_per_active_day) / 365.0

    category, desc = _categorize(rpd)
    return FrequencyAnalysis(
        expression=expression,
        is_valid=True,
        estimated_runs_per_day=round(rpd, 4),
        category=category,
        description=desc,
    )


def _categorize(rpd: Optional[float]):
    if rpd is None:
        return "rare", "indeterminate frequency"
    for threshold, cat, desc in _CATEGORY_THRESHOLDS:
        if rpd >= threshold:
            return cat, desc
    return "rare", "once per week or less"
