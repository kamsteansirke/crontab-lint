"""CLI entry point for the pattern-match sub-command."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .pattern_matcher import match
from .pattern_matcher_formatter import format_matches, format_summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-pattern",
        description="Find cron expressions that match a natural-language description.",
    )
    p.add_argument(
        "query",
        nargs="+",
        help="Natural-language description, e.g. 'run daily at midnight'",
    )
    p.add_argument(
        "-n",
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Maximum number of results to show (default: 5)",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary instead of full results",
    )
    return p


def run_pattern(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    query = " ".join(args.query)
    results = match(query, top_n=args.top)

    if args.summary:
        print(format_summary(results))
    else:
        print(format_matches(results, query=query))

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run_pattern())


if __name__ == "__main__":  # pragma: no cover
    main()
