"""Formatting helpers for RuleCheckResult output."""
from __future__ import annotations

from typing import List

from .rule_checker import RuleCheckResult, RuleViolation


def format_violation(v: RuleViolation) -> str:
    return f"  [FAIL] {v.rule_name}: {v.message}"


def format_result(result: RuleCheckResult) -> str:
    lines: List[str] = []
    status = "PASS" if result.passed else "FAIL"
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Status     : {status}")
    if result.violations:
        lines.append("Violations :")
        for v in result.violations:
            lines.append(format_violation(v))
    return "\n".join(lines)


def format_results(results: List[RuleCheckResult]) -> str:
    blocks = [format_result(r) for r in results]
    return "\n\n".join(blocks)


def format_summary(results: List[RuleCheckResult]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    return f"Rule check summary: {total} checked, {passed} passed, {failed} failed."
