"""Formatters for expression retention policy results."""
from __future__ import annotations

from typing import List

from .expression_retention import RetentionResult, RetentionViolation

_PASS = "\u2713"
_FAIL = "\u2717"


def format_violation(violation: RetentionViolation) -> str:
    return f"  [{violation.rule}] {violation.message}"


def format_result(result: RetentionResult, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""

    if not result.is_valid:
        return (
            f"{prefix}{_FAIL} {result.expression}\n"
            f"  ERROR: {result.error}"
        )

    status = _PASS if result.passed else _FAIL
    rpd_str = f"{result.runs_per_day:.2f}" if result.runs_per_day is not None else "?"
    lines = [f"{prefix}{status} {result.expression}  ({rpd_str} runs/day)"]

    for v in result.violations:
        lines.append(format_violation(v))

    return "\n".join(lines)


def format_results(results: List[RetentionResult]) -> str:
    parts = [
        format_result(r, index=i + 1) for i, r in enumerate(results)
    ]
    return "\n".join(parts)


def format_summary(results: List[RetentionResult]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    lines = [
        "Retention Policy Summary",
        f"  Total   : {total}",
        f"  Passed  : {passed}",
        f"  Failed  : {failed}",
    ]
    return "\n".join(lines)
