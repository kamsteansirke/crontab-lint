"""CLI entry point for batch expression validation with a summary report."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .expression_validator_report import validate_expressions
from .expression_validator_report_formatter import format_report, format_summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-validate-report",
        description="Validate one or more crontab expressions and print a report.",
    )
    p.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to validate.",
    )
    p.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    p.add_argument(
        "--summary-only", "-s",
        action="store_true",
        help="Print only the summary line.",
    )
    return p


def run_validate_report(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions or [])

    if args.file:
        try:
            with open(args.file) as fh:
                expressions.extend(fh.readlines())
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 1

    if not expressions:
        parser.print_help()
        return 0

    report = validate_expressions(expressions)

    if not args.summary_only:
        print(format_report(report))
        print()
    print(format_summary(report))

    return 0 if report.all_valid else 2


def main() -> None:  # pragma: no cover
    sys.exit(run_validate_report())
