"""CLI sub-command: export lint results as JSON or CSV."""
from __future__ import annotations
import argparse
import sys
from typing import List

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain
from crontab_lint.formatter import LintResult
from crontab_lint.exporter import export


def _lint(expression: str) -> LintResult:
    try:
        cron = parse(expression)
        explanation = explain(cron)
        return LintResult(expression=expression, valid=True, errors=[], explanation=explanation)
    except ParseError as exc:
        return LintResult(expression=expression, valid=False, errors=[str(exc)], explanation="")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-export",
        description="Export crontab lint results to JSON or CSV.",
    )
    p.add_argument("expressions", nargs="*", help="Cron expressions to lint")
    p.add_argument("-f", "--file", help="File containing one expression per line")
    p.add_argument("-F", "--format", choices=["json", "csv"], default="json", dest="fmt")
    return p


def run_export(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)

    if args.file:
        try:
            with open(args.file) as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        expressions.append(line)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 1

    if not expressions:
        parser.print_help()
        return 0

    results = [_lint(expr) for expr in expressions]
    print(export(results, args.fmt))
    return 0


def main() -> None:
    sys.exit(run_export())


if __name__ == "__main__":
    main()
