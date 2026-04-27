"""CLI entry point for comparing two crontab expressions."""
import argparse
import sys
from crontab_lint.expression_comparator import compare
from crontab_lint.expression_comparator_formatter import format_comparison, format_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-compare",
        description="Compare two crontab expressions field-by-field.",
    )
    parser.add_argument("left", help="First cron expression")
    parser.add_argument("right", help="Second cron expression")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary instead of full output",
    )
    return parser


def run_compare(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = compare(args.left, args.right)

    if args.summary:
        print(format_summary([result]))
    else:
        print(format_comparison(result))

    return 0 if result.valid else 1


def main() -> None:
    sys.exit(run_compare())


if __name__ == "__main__":
    main()
