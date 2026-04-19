"""CLI for managing tagged crontab expressions."""
import argparse
import json
import sys
from pathlib import Path
from typing import List

from crontab_lint.tag_manager import TagRegistry, registry_from_list


def _load_registry(path: str) -> TagRegistry:
    p = Path(path)
    if not p.exists():
        return TagRegistry()
    with open(p) as f:
        data = json.load(f)
    return registry_from_list(data)


def _save_registry(registry: TagRegistry, path: str) -> None:
    data = [
        {
            "expression": e.expression,
            "tags": e.tags,
            "description": e.description,
        }
        for e in registry.entries
    ]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage tagged crontab expressions")
    parser.add_argument("--file", default="crontags.json", help="Tag registry file")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a tagged expression")
    add_p.add_argument("expression")
    add_p.add_argument("--tags", nargs="+", default=[])
    add_p.add_argument("--description", default=None)

    find_p = sub.add_parser("find", help="Find expressions by tag")
    find_p.add_argument("tag")

    sub.add_parser("list-tags", help="List all tags")

    rm_p = sub.add_parser("remove", help="Remove an expression")
    rm_p.add_argument("expression")

    return parser


def run_tags(args: List[str]) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)
    if not ns.command:
        parser.print_help()
        return 0

    registry = _load_registry(ns.file)

    if ns.command == "add":
        registry.add(ns.expression, ns.tags, ns.description)
        _save_registry(registry, ns.file)
        print(f"Added: {ns.expression} tags={ns.tags}")

    elif ns.command == "find":
        results = registry.find_by_tag(ns.tag)
        if not results:
            print(f"No expressions found with tag '{ns.tag}'")
        for e in results:
            desc = f" — {e.description}" if e.description else ""
            print(f"  {e.expression} [{', '.join(e.tags)}]{desc}")

    elif ns.command == "list-tags":
        tags = registry.all_tags()
        if not tags:
            print("No tags registered.")
        for t in tags:
            print(f"  {t}")

    elif ns.command == "remove":
        removed = registry.remove_by_expression(ns.expression)
        _save_registry(registry, ns.file)
        print(f"Removed {removed} entry(s) for: {ns.expression}")

    return 0


def main():
    sys.exit(run_tags(sys.argv[1:]))


if __name__ == "__main__":
    main()
