"""Rule-based checker for crontab expressions against user-defined policies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse, ParseError


@dataclass
class Rule:
    name: str
    description: str
    # e.g. {"minute": "*/1"} means "minute must not be every-minute wildcard step"
    forbidden_patterns: dict = field(default_factory=dict)
    max_frequency_minutes: Optional[int] = None


@dataclass
class RuleViolation:
    rule_name: str
    message: str


@dataclass
class RuleCheckResult:
    expression: str
    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _estimate_frequency_minutes(expr: CronExpression) -> Optional[int]:
    """Rough lower-bound estimate of how often the expression fires (in minutes)."""
    minute_field = expr.fields[0]
    if minute_field == "*":
        return 1
    if minute_field.startswith("*/"):
        try:
            return int(minute_field[2:])
        except ValueError:
            return None
    return None


def check_expression(raw: str, rules: List[Rule]) -> RuleCheckResult:
    """Check a single crontab expression against a list of rules."""
    result = RuleCheckResult(expression=raw)
    try:
        expr = parse(raw)
    except ParseError as exc:
        result.violations.append(RuleViolation(rule_name="parse", message=str(exc)))
        return result

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]

    for rule in rules:
        for fname, pattern in rule.forbidden_patterns.items():
            try:
                idx = field_names.index(fname)
            except ValueError:
                continue
            if expr.fields[idx] == pattern:
                result.violations.append(
                    RuleViolation(
                        rule_name=rule.name,
                        message=f"{rule.description}: field '{fname}' matches forbidden pattern '{pattern}'",
                    )
                )

        if rule.max_frequency_minutes is not None:
            freq = _estimate_frequency_minutes(expr)
            if freq is not None and freq < rule.max_frequency_minutes:
                result.violations.append(
                    RuleViolation(
                        rule_name=rule.name,
                        message=(
                            f"{rule.description}: expression fires every ~{freq} minute(s), "
                            f"minimum allowed interval is {rule.max_frequency_minutes} minute(s)"
                        ),
                    )
                )

    return result


def check_many(expressions: List[str], rules: List[Rule]) -> List[RuleCheckResult]:
    """Check multiple expressions against the given rules."""
    return [check_expression(expr, rules) for expr in expressions]
