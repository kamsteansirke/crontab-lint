"""CLI for browsing and using built-in crontab templates."""
import argparse
import sys
from crontab_lint.template_library import list_templates, find_by_name, find_by_tag, search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-templates",
        description="Browse built-in crontab expression templates",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all templates")

    get_p = sub.add_parser("get", help="Get a template by name")
    get_p.add_argument("name", help="Template name")

    tag_p = sub.add_parser("tag", help="Find templates by tag")
    tag_p.add_argument("tag", help="Tag to filter by")

    search_p = sub.add_parser("search", help="Search templates")
    search_p.add_argument("query", help="Search query")

    return parser


def _print_template(t) -> None:
    print(f"  {t.name:<20} {t.expression:<20} {t.description}")
    if t.tags:
        print(f"  {'':20} tags: {', '.join(t.tags)}")


def run_templates(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        templates = list_templates()
        print(f"{'NAME':<20} {'EXPRESSION':<20} DESCRIPTION")
        print("-" * 70)
        for t in templates:
            print(f"{t.name:<20} {t.expression:<20} {t.description}")
        return 0

    if args.command == "get":
        t = find_by_name(args.name)
        if t is None:
            print(f"Template not found: {args.name}", file=sys.stderr)
            return 1
        _print_template(t)
        return 0

    if args.command == "tag":
        results = find_by_tag(args.tag)
        if not results:
            print(f"No templates found with tag: {args.tag}")
            return 0
        for t in results:
            _print_template(t)
        return 0

    if args.command == "search":
        results = search(args.query)
        if not results:
            print(f"No templates matched: {args.query}")
            return 0
        for t in results:
            _print_template(t)
        return 0

    parser.print_help()
    return 0


def main():
    sys.exit(run_templates())
