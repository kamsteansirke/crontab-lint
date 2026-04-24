"""CLI entry point for the expression grouper."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .expression_grouper import group
from .expression_grouper_formatter import format_grouping, format_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-group",
        description="Group cron expressions by frequency category.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Cron expressions to group (or read from stdin).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after the groups.",
    )
    return parser


def run_group(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.expressions:
        expressions = args.expressions
    elif not sys.stdin.isatty():
        expressions = [line.rstrip("\n") for line in sys.stdin]
    else:
        parser.print_help()
        return 0

    result = group(expressions)
    output = format_grouping(result)
    if output:
        print(output)
    if args.summary:
        print(format_summary(result))
    return 0


def main() -> None:
    sys.exit(run_group())


if __name__ == "__main__":
    main()
