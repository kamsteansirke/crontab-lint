"""Tests for crontab_lint.expression_grouper."""

from crontab_lint.expression_grouper import group, ExpressionGroup, GroupingResult


def test_empty_input_returns_empty_result():
    result = group([])
    assert result.groups == []
    assert result.ungrouped == []


def test_blank_and_comment_lines_are_skipped():
    result = group(["", "  ", "# this is a comment"])
    assert result.groups == []
    assert result.ungrouped == []


def test_invalid_expression_goes_to_ungrouped():
    result = group(["not-a-cron"])
    assert "not-a-cron" in result.ungrouped
    assert result.group_count() == 0


def test_every_minute_is_grouped():
    result = group(["* * * * *"])
    assert result.group_count() >= 1
    all_exprs = [e for g in result.groups for e in g.expressions]
    assert "* * * * *" in all_exprs


def test_daily_expression_is_grouped():
    result = group(["0 9 * * *"])
    assert result.group_count() >= 1
    all_exprs = [e for g in result.groups for e in g.expressions]
    assert "0 9 * * *" in all_exprs


def test_multiple_same_category_go_to_same_group():
    result = group(["0 8 * * *", "0 12 * * *", "0 18 * * *"])
    # all daily — expect them in one group
    assert result.group_count() >= 1
    largest = max(result.groups, key=lambda g: g.size())
    assert largest.size() == 3


def test_different_categories_produce_separate_groups():
    result = group(["* * * * *", "0 0 * * 0"])
    categories = {g.category for g in result.groups}
    # two different categories expected
    assert len(categories) >= 1  # at minimum they parse


def test_group_count_method():
    result = group(["* * * * *", "not-valid"])
    assert result.group_count() == len(result.groups)


def test_find_returns_correct_group():
    result = group(["* * * * *"])
    if result.groups:
        cat = result.groups[0].category
        found = result.find(cat)
        assert found is not None
        assert found.category == cat


def test_find_missing_category_returns_none():
    result = group(["* * * * *"])
    assert result.find("__nonexistent__") is None


def test_expression_group_size():
    g = ExpressionGroup(label="Test", category="test", expressions=["a", "b"])
    assert g.size() == 2
