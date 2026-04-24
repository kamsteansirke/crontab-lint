"""Normalize crontab expressions to a canonical form."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .parser import parse, ParseError

# Maps special strings to their 5-field equivalents
_SPECIAL_MAP: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

_DOW_NAMES = {"sun": "0", "mon": "1", "tue": "2", "wed": "3",
              "thu": "4", "fri": "5", "sat": "6"}
_MON_NAMES = {"jan": "1", "feb": "2", "mar": "3", "apr": "4",
              "may": "5", "jun": "6", "jul": "7", "aug": "8",
              "sep": "9", "oct": "10", "nov": "11", "dec": "12"}


@dataclass
class NormalizeResult:
    original: str
    normalized: Optional[str]
    changed: bool
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _replace_names(field: str, mapping: dict[str, str]) -> str:
    result = field
    for name, num in mapping.items():
        result = result.replace(name, num)
    return result


def _normalize_field(field: str, index: int) -> str:
    """Normalize a single cron field."""
    field = field.strip().lower()
    if index == 4:  # day-of-week
        field = _replace_names(field, _DOW_NAMES)
    elif index == 3:  # month
        field = _replace_names(field, _MON_NAMES)
    # Normalize */1 to *
    if field == "*/1":
        field = "*"
    return field


def normalize(expression: str) -> NormalizeResult:
    """Return a canonical form of the given cron expression."""
    expr = expression.strip()

    # Expand special strings
    lower = expr.lower()
    if lower in _SPECIAL_MAP:
        normalized = _SPECIAL_MAP[lower]
        return NormalizeResult(original=expression, normalized=normalized, changed=True)

    try:
        parsed = parse(expr)
    except ParseError as exc:
        return NormalizeResult(original=expression, normalized=None, changed=False, error=str(exc))

    fields = [parsed.minute, parsed.hour, parsed.day_of_month, parsed.month, parsed.day_of_week]
    normalized_fields = [_normalize_field(f, i) for i, f in enumerate(fields)]

    if parsed.command:
        normalized = " ".join(normalized_fields) + " " + parsed.command
    else:
        normalized = " ".join(normalized_fields)

    changed = normalized != expr
    return NormalizeResult(original=expression, normalized=normalized, changed=changed)
