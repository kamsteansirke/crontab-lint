"""CLI subcommand for displaying next scheduled run times."""

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from .scheduler import next_n_runs, ScheduleError
from .schedule_formatter import format_schedule_block


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-schedule",
        description="Show the next N run times for a cron expression.",
    )
    parser.add_argument("expression", nargs="+", help="Cron expression (quote if needed)")
    parser.add_argument(
        "-n", "--count", type=int, default=5, help="Number of upcoming runs to show (default: 5)"
    )
    parser.add_argument(
        "--after",
        type=str,
        default=None,
        help="Compute runs after this datetime (format: YYYY-MM-DD HH:MM)",
    )
    return parser


def run_schedule(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args)

    expression = " ".join(parsed.expression)
    after: Optional[datetime] = None

    if parsed.after:
        try:
            after = datetime.strptime(parsed.after, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Invalid --after format. Use YYYY-MM-DD HH:MM", file=sys.stderr)
            return 2

    try:
        runs = next_n_runs(expression, n=parsed.count, after=after)
        print(format_schedule_block(expression, runs))
        return 0
    except ScheduleError as e:
        print(format_schedule_block(expression, [], error=str(e)))
        return 1


def main() -> None:
    sys.exit(run_schedule())


if __name__ == "__main__":
    main()
