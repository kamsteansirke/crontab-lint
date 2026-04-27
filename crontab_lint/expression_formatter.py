"""Pretty-print a cron expression as a structured, human-readable table."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain

_FIELD_NAMES = ["Minute", "Hour", "Day (month)", "Month", "Day (week)"]
_FIELD_RANGES = ["0-59", "0-23", "1-31", "1-12", "0-6"]


@dataclass
class FieldRow:
    name: str
    value: str
    allowed_range: str


@dataclass
class FormattedExpression:
    raw: str
    is_valid: bool
    error: str | None
    fields: List[FieldRow]
    explanation: str | None

    @property
    def ok(self) -> bool:
        return self.is_valid


def format_expression(expression: str) -> FormattedExpression:
    """Parse *expression* and return a structured representation."""
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return FormattedExpression(
            raw=expression,
            is_valid=False,
            error=str(exc),
            fields=[],
            explanation=None,
        )

    raw_fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]

    rows = [
        FieldRow(name=name, value=value, allowed_range=rng)
        for name, value, rng in zip(_FIELD_NAMES, raw_fields, _FIELD_RANGES)
    ]

    return FormattedExpression(
        raw=expression,
        is_valid=True,
        error=None,
        fields=rows,
        explanation=explain(parsed),
    )


def render_table(fmt: FormattedExpression) -> str:
    """Return a multi-line string table for *fmt*."""
    if not fmt.is_valid:
        return f"Expression : {fmt.raw}\nStatus     : INVALID\nError      : {fmt.error}\n"

    col_w = max(len(r.name) for r in fmt.fields)
    lines = [f"Expression : {fmt.raw}", f"Status     : valid"]
    lines.append("-" * 42)
    lines.append(f"{'Field':<{col_w}}  {'Value':<12}  Range")
    lines.append("-" * 42)
    for row in fmt.fields:
        lines.append(f"{row.name:<{col_w}}  {row.value:<12}  {row.allowed_range}")
    lines.append("-" * 42)
    if fmt.explanation:
        lines.append(f"Meaning    : {fmt.explanation}")
    return "\n".join(lines) + "\n"
