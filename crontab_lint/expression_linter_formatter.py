"""Formatter for AggregateLintResult."""
from __future__ import annotations

from typing import List

from .expression_linter import AggregateLintResult, LintIssue

_SEVERITY_PREFIX = {
    "error": "[ERROR]",
    "warning": "[WARN] ",
    "info": "[INFO] ",
}


def format_issue(issue: LintIssue) -> str:
    prefix = _SEVERITY_PREFIX.get(issue.severity, "[?]   ")
    return f"  {prefix} ({issue.category}) {issue.message}"


def format_result(result: AggregateLintResult, *, show_score: bool = True) -> str:
    lines: List[str] = []
    status = "VALID" if result.is_valid else "INVALID"
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Status     : {status}")

    if result.explanation:
        lines.append(f"Explanation: {result.explanation}")

    if result.score and show_score:
        lines.append(
            f"Score      : {result.score.total}/100  (grade {result.score.grade})"
        )

    if result.issues:
        lines.append(f"Issues ({result.issue_count}):")
        for issue in result.issues:
            lines.append(format_issue(issue))
    else:
        lines.append("Issues     : none")

    return "\n".join(lines)


def format_results(results: List[AggregateLintResult], *, show_score: bool = True) -> str:
    blocks = [format_result(r, show_score=show_score) for r in results]
    return "\n\n".join(blocks)


def format_summary(results: List[AggregateLintResult]) -> str:
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    with_issues = sum(1 for r in results if r.issue_count > 0)
    lines = [
        f"Total      : {total}",
        f"Valid      : {valid}",
        f"Invalid    : {total - valid}",
        f"With issues: {with_issues}",
    ]
    return "\n".join(lines)
