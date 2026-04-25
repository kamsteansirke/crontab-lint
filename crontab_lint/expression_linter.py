"""Aggregate linter that runs multiple checks on a crontab expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .explainer import explain
from .rule_checker import RuleCheckResult, check_expression, Rule
from .env_validator import EnvValidationResult, validate as env_validate, EnvConstraint
from .expression_scorer import ExpressionScore, score
from .timezone_checker import TimezoneCheckResult, check as tz_check


@dataclass
class LintIssue:
    category: str
    message: str
    severity: str = "warning"  # "error" | "warning" | "info"


@dataclass
class AggregateLintResult:
    expression: str
    is_valid: bool
    explanation: Optional[str]
    issues: List[LintIssue] = field(default_factory=list)
    score: Optional[ExpressionScore] = None
    rule_result: Optional[RuleCheckResult] = None
    env_result: Optional[EnvValidationResult] = None
    tz_result: Optional[TimezoneCheckResult] = None

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def lint(
    expression: str,
    rules: Optional[List[Rule]] = None,
    constraints: Optional[List[EnvConstraint]] = None,
    timezone: Optional[str] = None,
) -> AggregateLintResult:
    """Run all available checks and return an aggregated result."""
    issues: List[LintIssue] = []

    # Parse / validate
    try:
        parse(expression)
        is_valid = True
        explanation = explain(expression)
    except ParseError as exc:
        is_valid = False
        explanation = None
        issues.append(LintIssue("parse", str(exc), "error"))
        return AggregateLintResult(
            expression=expression,
            is_valid=False,
            explanation=None,
            issues=issues,
        )

    # Scoring
    expr_score = score(expression)

    # Rule checking
    rule_result: Optional[RuleCheckResult] = None
    if rules:
        rule_result = check_expression(expression, rules)
        for v in rule_result.violations:
            issues.append(LintIssue("rule", f"{v.rule.name}: {v.message}", "warning"))

    # Env constraints
    env_result: Optional[EnvValidationResult] = None
    if constraints:
        env_result = env_validate(expression, constraints)
        for v in env_result.violations:
            issues.append(LintIssue("env", v.message, "warning"))

    # Timezone
    tz_result: Optional[TimezoneCheckResult] = None
    if timezone:
        tz_result = tz_check(expression, timezone)
        for w in tz_result.warnings:
            issues.append(LintIssue("timezone", w.message, "info"))

    return AggregateLintResult(
        expression=expression,
        is_valid=is_valid,
        explanation=explanation,
        issues=issues,
        score=expr_score,
        rule_result=rule_result,
        env_result=env_result,
        tz_result=tz_result,
    )
