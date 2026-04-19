"""Output formatting for crontab-lint results."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LintResult:
    expression: str
    command: Optional[str]
    valid: bool
    explanation: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def format_result(result: LintResult, *, color: bool = True) -> str:
    """Format a LintResult as a human-readable string."""
    lines = []

    status = "\u2705 VALID" if result.valid else "\u274c INVALID"
    if color:
        status = f"\033[92m{status}\033[0m" if result.valid else f"\033[91m{status}\033[0m"

    lines.append(f"{status}  {result.expression}")

    if result.command:
        lines.append(f"  Command    : {result.command}")

    if result.explanation:
        lines.append(f"  Explanation: {result.explanation}")

    for err in result.errors:
        prefix = "\033[91m  ERROR\033[0m  :" if color else "  ERROR  :"
        lines.append(f"{prefix} {err}")

    for warn in result.warnings:
        prefix = "\033[93m  WARN\033[0m   :" if color else "  WARN   :"
        lines.append(f"{prefix} {warn}")

    return "\n".join(lines)


def format_results(results: List[LintResult], *, color: bool = True) -> str:
    """Format multiple LintResults separated by blank lines."""
    return "\n\n".join(format_result(r, color=color) for r in results)


def format_summary(results: List[LintResult], *, color: bool = True) -> str:
    """Format a summary line showing how many expressions passed and failed."""
    total = len(results)
    valid = sum(1 for r in results if r.valid)
    invalid = total - valid

    if color:
        valid_str = f"\033[92m{valid} valid\033[0m"
        invalid_str = f"\033[91m{invalid} invalid\033[0m"
    else:
        valid_str = f"{valid} valid"
        invalid_str = f"{invalid} invalid"

    return f"Summary: {total} expression(s) checked — {valid_str}, {invalid_str}"
