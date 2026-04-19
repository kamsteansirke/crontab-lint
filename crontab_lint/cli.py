"""CLI entry point for crontab-lint."""
import sys
import argparse
from typing import List

from .parser import parse, ParseError
from .explainer import explain
from .formatter import LintResult, format_result, format_results
from .conflict_detector import detect_conflicts


def lint_expression(expression: str) -> LintResult:
    """Lint a single crontab expression and return a LintResult."""
    try:
        cron = parse(expression)
        explanation = explain(cron)
        return LintResult(
            expression=expression,
            valid=True,
            explanation=explanation,
            errors=[],
        )
    except ParseError as e:
        return LintResult(
            expression=expression,
            valid=False,
            explanation=None,
            errors=[str(e)],
        )


def run(argv: List[str] = None) -> int:
    """Main CLI runner. Returns exit code."""
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Crontab expression(s) to lint.",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    parser.add_argument(
        "--conflicts", "-c",
        action="store_true",
        help="Detect scheduling conflicts between multiple expressions.",
    )
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)

    if args.file:
        try:
            with open(args.file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        expressions.append(line)
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 0

    results = [lint_expression(expr) for expr in expressions]
    print(format_results(results))

    if args.conflicts and len(expressions) > 1:
        parsed_crons = []
        for expr in expressions:
            try:
                parsed_crons.append(parse(expr))
            except ParseError:
                pass
        if len(parsed_crons) > 1:
            report = detect_conflicts(parsed_crons)
            if report.conflicts:
                print("\nConflicts detected:")
                for conflict in report.conflicts:
                    print(f"  - {conflict.description}")
            else:
                print("\nNo conflicts detected.")

    all_valid = all(r.valid for r in results)
    return 0 if all_valid else 1


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
