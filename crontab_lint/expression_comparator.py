"""Compare two crontab expressions field-by-field and report differences."""
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldDiff:
    name: str
    left: str
    right: str
    changed: bool


@dataclass
class ComparisonResult:
    left: str
    right: str
    valid: bool
    error: Optional[str]
    field_diffs: List[FieldDiff] = field(default_factory=list)
    left_explanation: Optional[str] = None
    right_explanation: Optional[str] = None

    @property
    def has_differences(self) -> bool:
        return any(d.changed for d in self.field_diffs)

    @property
    def changed_fields(self) -> List[FieldDiff]:
        return [d for d in self.field_diffs if d.changed]


def compare(left: str, right: str) -> ComparisonResult:
    """Compare two cron expressions and return a detailed field-by-field diff."""
    try:
        left_expr = parse(left)
        right_expr = parse(right)
    except ParseError as exc:
        return ComparisonResult(
            left=left,
            right=right,
            valid=False,
            error=str(exc),
        )

    left_fields = [
        left_expr.minute,
        left_expr.hour,
        left_expr.day_of_month,
        left_expr.month,
        left_expr.day_of_week,
    ]
    right_fields = [
        right_expr.minute,
        right_expr.hour,
        right_expr.day_of_month,
        right_expr.month,
        right_expr.day_of_week,
    ]

    diffs = [
        FieldDiff(
            name=name,
            left=lf,
            right=rf,
            changed=lf != rf,
        )
        for name, lf, rf in zip(FIELD_NAMES, left_fields, right_fields)
    ]

    return ComparisonResult(
        left=left,
        right=right,
        valid=True,
        error=None,
        field_diffs=diffs,
        left_explanation=explain(left_expr),
        right_explanation=explain(right_expr),
    )
