"""Summarize differences between two lists of cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain


@dataclass
class DiffSummaryEntry:
    expression: str
    status: str  # 'added', 'removed', 'unchanged'
    explanation: str | None = None


@dataclass
class ExpressionDiffSummary:
    added: List[DiffSummaryEntry] = field(default_factory=list)
    removed: List[DiffSummaryEntry] = field(default_factory=list)
    unchanged: List[DiffSummaryEntry] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed)

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0

    @property
    def all_entries(self) -> List[DiffSummaryEntry]:
        return self.added + self.removed + self.unchanged


def _safe_explain(expression: str) -> str | None:
    try:
        parsed = parse(expression)
        return explain(parsed)
    except (ParseError, Exception):
        return None


def _normalize(line: str) -> str:
    return line.strip()


def _skip(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def diff_expression_lists(
    before: List[str],
    after: List[str],
) -> ExpressionDiffSummary:
    """Compare two lists of cron expression strings and return a structured diff."""
    before_set = {_normalize(e) for e in before if not _skip(e)}
    after_set = {_normalize(e) for e in after if not _skip(e)}

    added_exprs = after_set - before_set
    removed_exprs = before_set - after_set
    unchanged_exprs = before_set & after_set

    summary = ExpressionDiffSummary()

    for expr in sorted(added_exprs):
        summary.added.append(
            DiffSummaryEntry(expr, "added", _safe_explain(expr))
        )
    for expr in sorted(removed_exprs):
        summary.removed.append(
            DiffSummaryEntry(expr, "removed", _safe_explain(expr))
        )
    for expr in sorted(unchanged_exprs):
        summary.unchanged.append(
            DiffSummaryEntry(expr, "unchanged", _safe_explain(expr))
        )

    return summary
