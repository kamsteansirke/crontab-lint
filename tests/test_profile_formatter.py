"""Tests for crontab_lint.profile_formatter."""
from crontab_lint.profile import Profile
from crontab_lint.profile_formatter import (
    format_profile,
    format_profiles,
    format_summary,
)


def _make(name="test", description="", expressions=None, tags=None) -> Profile:
    return Profile(
        name=name,
        description=description,
        expressions=expressions or [],
        tags=tags or [],
    )


def test_format_profile_contains_name():
    p = _make(name="nightly")
    assert "nightly" in format_profile(p)


def test_format_profile_contains_description():
    p = _make(description="Runs every night")
    assert "Runs every night" in format_profile(p)


def test_format_profile_contains_tags():
    p = _make(tags=["prod", "nightly"])
    out = format_profile(p)
    assert "prod" in out
    assert "nightly" in out


def test_format_profile_lists_expressions():
    p = _make(expressions=["0 0 * * *", "*/5 * * * *"])
    out = format_profile(p)
    assert "0 0 * * *" in out
    assert "*/5 * * * *" in out


def test_format_profile_no_expressions_message():
    p = _make()
    assert "(none)" in format_profile(p)


def test_format_profile_with_index():
    p = _make(name="alpha")
    out = format_profile(p, index=3)
    assert out.startswith("3.")


def test_format_profiles_empty():
    assert "No profiles" in format_profiles([])


def test_format_profiles_multiple():
    profiles = [_make(name="a"), _make(name="b")]
    out = format_profiles(profiles)
    assert "[a]" in out
    assert "[b]" in out


def test_format_profiles_numbered():
    profiles = [_make(name="first"), _make(name="second")]
    out = format_profiles(profiles)
    assert "1." in out
    assert "2." in out


def test_format_summary_counts():
    profiles = [
        _make(expressions=["0 0 * * *", "*/5 * * * *"]),
        _make(expressions=["0 12 * * 1"]),
    ]
    out = format_summary(profiles)
    assert "2 profile" in out
    assert "3 expression" in out
