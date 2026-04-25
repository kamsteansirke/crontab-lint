"""CLI entry-point for the calendar view feature."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .expression_calendar import build_calendar
from .expression_calendar_formatter import format_calendar, format_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-calendar",
        description="Show a day-by-day calendar of cron expression runs.",
    )
    parser.add_argument("expressions", nargs="+", help="Cron expression(s) to visualise")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to display (default: 7)",
    )
    parser.add_argument(
        "--start",
        default=None,
        metavar="YYYY-MM-DD",
        help="Start date (default: today)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary per expression instead of full calendar",
    )
    return parser


def run_calendar(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    start: datetime | None = None
    if args.start:
        try:
            start = datetime.strptime(args.start, "%Y-%m-%d")
        except ValueError:
            print(f"ERROR: invalid date '{args.start}', expected YYYY-MM-DD", file=sys.stderr)
            return 1

    views = [
        build_calendar(expr, start=start, days=args.days)
        for expr in args.expressions
    ]

    if args.summary:
        print(format_summary(views))
    else:
        for view in views:
            print(format_calendar(view))
            print()

    return 0


def main() -> None:
    sys.exit(run_calendar())
