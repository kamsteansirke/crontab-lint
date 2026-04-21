"""Generates human-readable overlap reports between cron expressions."""

from dataclasses import dataclass, field
from typing import List

from crontab_lint.conflict_detector import ConflictReport, detect_conflicts
from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain


@dataclass
class OverlapEntry:
    expression_a: str
    expression_b: str
    overlapping_fields: List[str]
    explanation_a: str = ""
    explanation_b: str = ""


@dataclass
class OverlapReport:
    entries: List[OverlapEntry] = field(default_factory=list)

    @property
    def has_overlaps(self) -> bool:
        return len(self.entries) > 0

    @property
    def count(self) -> int:
        return len(self.entries)


def _safe_explain(expression: str) -> str:
    try:
        result = parse(expression)
        return explain(result)
    except ParseError:
        return "(invalid expression)"


def build_overlap_report(expressions: List[str]) -> OverlapReport:
    """Check all pairs of expressions for scheduling overlaps."""
    report = OverlapReport()
    parsed = []
    for expr in expressions:
        try:
            parsed.append((expr, parse(expr)))
        except ParseError:
            parsed.append((expr, None))

    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            expr_a, cron_a = parsed[i]
            expr_b, cron_b = parsed[j]
            if cron_a is None or cron_b is None:
                continue
            conflict_report: ConflictReport = detect_conflicts([cron_a, cron_b])
            if conflict_report.has_conflicts:
                overlapping = [
                    c.field_name
                    for c in conflict_report.conflicts
                ]
                entry = OverlapEntry(
                    expression_a=expr_a,
                    expression_b=expr_b,
                    overlapping_fields=overlapping,
                    explanation_a=_safe_explain(expr_a),
                    explanation_b=_safe_explain(expr_b),
                )
                report.entries.append(entry)

    return report


def format_overlap_report(report: OverlapReport) -> str:
    """Format an OverlapReport as a human-readable string."""
    if not report.has_overlaps:
        return "No overlapping expressions detected."

    lines = [f"Found {report.count} overlapping pair(s):\n"]
    for idx, entry in enumerate(report.entries, start=1):
        lines.append(f"  [{idx}] {entry.expression_a}")
        lines.append(f"       {entry.explanation_a}")
        lines.append(f"      vs.")
        lines.append(f"       {entry.expression_b}")
        lines.append(f"       {entry.explanation_b}")
        fields = ", ".join(entry.overlapping_fields) if entry.overlapping_fields else "(all)"
        lines.append(f"      Overlapping fields: {fields}")
        lines.append("")
    return "\n".join(lines)
