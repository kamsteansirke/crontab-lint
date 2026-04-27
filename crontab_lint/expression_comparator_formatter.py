"""Formatting helpers for ComparisonResult objects."""
from typing import List
from crontab_lint.expression_comparator import ComparisonResult, FieldDiff

_CHANGED = "~ "
_SAME = "  "


def format_field_diff(diff: FieldDiff) -> str:
    marker = _CHANGED if diff.changed else _SAME
    if diff.changed:
        return f"{marker}{diff.name:15s}  {diff.left!r:20s} -> {diff.right!r}"
    return f"{marker}{diff.name:15s}  {diff.left!r}"


def format_comparison(result: ComparisonResult) -> str:
    lines: List[str] = []
    lines.append(f"Left : {result.left}")
    lines.append(f"Right: {result.right}")

    if not result.valid:
        lines.append(f"[ERROR] {result.error}")
        return "\n".join(lines)

    lines.append("")
    if result.left_explanation:
        lines.append(f"Left explanation : {result.left_explanation}")
    if result.right_explanation:
        lines.append(f"Right explanation: {result.right_explanation}")

    lines.append("")
    lines.append("Field comparison:")
    for diff in result.field_diffs:
        lines.append("  " + format_field_diff(diff))

    lines.append("")
    if result.has_differences:
        changed = ", ".join(d.name for d in result.changed_fields)
        lines.append(f"Changed fields: {changed}")
    else:
        lines.append("Expressions are identical in all fields.")

    return "\n".join(lines)


def format_comparisons(results: List[ComparisonResult]) -> str:
    return "\n\n".join(format_comparison(r) for r in results)


def format_summary(results: List[ComparisonResult]) -> str:
    total = len(results)
    identical = sum(1 for r in results if r.valid and not r.has_differences)
    different = sum(1 for r in results if r.valid and r.has_differences)
    errors = sum(1 for r in results if not r.valid)
    return (
        f"Comparisons: {total} | "
        f"Identical: {identical} | "
        f"Different: {different} | "
        f"Errors: {errors}"
    )
