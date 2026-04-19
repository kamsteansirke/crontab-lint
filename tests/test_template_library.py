import pytest
from crontab_lint.template_library import list_templates, find_by_name, find_by_tag, search
from crontab_lint.cli_templates import run_templates


def test_list_templates_nonempty():
    assert len(list_templates()) > 0


def test_list_templates_all_have_required_fields():
    for t in list_templates():
        assert t.name
        assert t.expression
        assert t.description


def test_find_by_name_existing():
    t = find_by_name("every-hour")
    assert t is not None
    assert t.expression == "0 * * * *"


def test_find_by_name_missing():
    assert find_by_name("nonexistent") is None


def test_find_by_tag_returns_matches():
    results = find_by_tag("daily")
    assert len(results) >= 2
    for t in results:
        assert "daily" in t.tags


def test_find_by_tag_no_match():
    assert find_by_tag("zzz-unknown") == []


def test_search_by_name():
    results = search("hourly")
    assert any(t.name == "every-hour" for t in results)


def test_search_by_description():
    results = search("midnight")
    assert len(results) >= 1


def test_search_no_match():
    assert search("xyzzy-nothing") == []


def test_cli_list_returns_zero():
    assert run_templates(["list"]) == 0


def test_cli_get_existing(capsys):
    rc = run_templates(["get", "yearly"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "yearly" in out


def test_cli_get_missing(capsys):
    rc = run_templates(["get", "no-such-template"])
    assert rc == 1


def test_cli_tag(capsys):
    rc = run_templates(["tag", "weekly"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "weekly-sunday" in out


def test_cli_search(capsys):
    rc = run_templates(["search", "minute"])
    assert rc == 0
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cli_no_command_returns_zero():
    assert run_templates([]) == 0
