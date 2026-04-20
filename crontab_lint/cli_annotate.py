"""CLI entry point for the annotator."""
import argparse
import sys
from crontab_lint.annotator import annotate, format_annotated


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-annotate",
        description="Annotate crontab expressions with human-readable comments.",
    )
    p.add_argument("file", nargs="?", help="Crontab file to annotate (default: stdin)")
    p.add_argument(
        "--comment-char", default="#", help="Character to use for inline comments"
    )
    p.add_argument(
        "--errors-only", action="store_true", help="Only show lines with errors"
    )
    return p


def run_annotate(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            with open(args.file) as f:
                lines = f.readlines()
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    else:
        lines = sys.stdin.readlines()

    annotated = annotate(lines)

    if args.errors_only:
        for entry in annotated:
            if not entry.is_valid:
                print(f"{entry.original.rstrip()}  {args.comment_char} {entry.annotation}")
        return 0

    print(format_annotated(annotated, comment_char=args.comment_char))
    return 0


def main():
    sys.exit(run_annotate())


if __name__ == "__main__":
    main()
