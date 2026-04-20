"""CLI for watching a crontab file and re-annotating on changes."""

import argparse
import sys
import time
import os
from typing import Optional

from crontab_lint.annotator import annotate, format_annotated


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the annotate-watch command."""
    parser = argparse.ArgumentParser(
        prog="crontab-annotate-watch",
        description="Watch a crontab file and re-annotate it whenever it changes.",
    )
    parser.add_argument(
        "file",
        help="Path to the crontab file to watch.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Annotate once and exit without watching for changes.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    return parser


def _read_lines(path: str) -> list[str]:
    """Read lines from a file, returning an empty list on error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.readlines()
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return []


def _annotate_and_print(path: str, use_color: bool) -> None:
    """Read, annotate, and print the contents of a crontab file."""
    lines = _read_lines(path)
    if not lines:
        return
    # Strip trailing newlines for annotation, then format
    stripped = [line.rstrip("\n") for line in lines]
    annotated = annotate(stripped)
    output = format_annotated(annotated)
    if not use_color:
        # Strip ANSI escape codes for plain output
        import re
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    print(output)


def _get_mtime(path: str) -> Optional[float]:
    """Return the modification time of a file, or None if unavailable."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def run_watch(args: argparse.Namespace) -> int:
    """Run the annotate-watch command.

    Returns 0 on success, 1 on error.
    """
    path = args.file
    interval = args.interval
    use_color = not args.no_color

    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    # Initial annotation
    _annotate_and_print(path, use_color)

    if args.once:
        return 0

    last_mtime = _get_mtime(path)
    print(f"\nWatching {path!r} for changes (interval: {interval}s). Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(interval)
            current_mtime = _get_mtime(path)
            if current_mtime is None:
                print(f"File disappeared: {path}", file=sys.stderr)
                return 1
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                print(f"--- {path} changed, re-annotating ---")
                _annotate_and_print(path, use_color)
    except KeyboardInterrupt:
        print("\nStopped watching.")

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the annotate-watch CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_watch(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
