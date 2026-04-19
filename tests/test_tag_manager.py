"""Tests for tag_manager module."""
import pytest
from crontab_lint.tag_manager import (
    TaggedExpression, TagRegistry, from_dict, registry_from_list
)


def test_tagged_expression_has_tag():
    te = TaggedExpression(expression="* * * * *", tags=["daily", "backup"])
    assert te.has_tag("daily")
    assert not te.has_tag("missing")


def test_registry_add():
    reg = TagRegistry()
    entry = reg.add("0 * * * *", ["hourly"], "Every hour")
    assert len(reg.entries) == 1
    assert entry.expression == "0 * * * *"
    assert entry.description == "Every hour"


def test_registry_find_by_tag():
    reg = TagRegistry()
    reg.add("0 * * * *", ["hourly"])
    reg.add("0 0 * * *", ["daily"])
    reg.add("*/5 * * * *", ["hourly", "frequent"])
    results = reg.find_by_tag("hourly")
    assert len(results) == 2
    assert all(e.has_tag("hourly") for e in results)


def test_registry_find_by_tag_empty():
    reg = TagRegistry()
    reg.add("* * * * *", ["misc"])
    assert reg.find_by_tag("nonexistent") == []


def test_registry_all_tags():
    reg = TagRegistry()
    reg.add("0 * * * *", ["hourly", "prod"])
    reg.add("0 0 * * *", ["daily", "prod"])
    tags = reg.all_tags()
    assert "hourly" in tags
    assert "daily" in tags
    assert "prod" in tags
    assert len(tags) == 3


def test_registry_remove_by_expression():
    reg = TagRegistry()
    reg.add("* * * * *", ["a"])
    reg.add("0 * * * *", ["b"])
    removed = reg.remove_by_expression("* * * * *")
    assert removed == 1
    assert len(reg.entries) == 1


def test_registry_remove_nonexistent():
    reg = TagRegistry()
    reg.add("* * * * *", ["a"])
    removed = reg.remove_by_expression("0 0 * * *")
    assert removed == 0


def test_from_dict_full():
    data = {"expression": "0 0 * * *", "tags": ["daily"], "description": "Midnight"}
    te = from_dict(data)
    assert te.expression == "0 0 * * *"
    assert te.tags == ["daily"]
    assert te.description == "Midnight"


def test_from_dict_minimal():
    data = {"expression": "* * * * *"}
    te = from_dict(data)
    assert te.tags == []
    assert te.description is None


def test_registry_from_list():
    items = [
        {"expression": "* * * * *", "tags": ["frequent"]},
        {"expression": "0 0 * * *", "tags": ["daily"], "description": "EOD"},
    ]
    reg = registry_from_list(items)
    assert len(reg.entries) == 2
    assert reg.find_by_tag("daily")[0].description == "EOD"
