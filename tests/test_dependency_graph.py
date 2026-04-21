"""Tests for dependency_graph and dependency_graph_formatter."""
import pytest
from crontab_lint.dependency_graph import build_graph, GraphEdge
from crontab_lint.dependency_graph_formatter import format_graph, format_summary


def test_no_expressions_produces_empty_graph():
    graph = build_graph([])
    assert graph.nodes == []
    assert graph.edges == []


def test_single_expression_no_edges():
    graph = build_graph([("* * * * *", "all")])
    assert len(graph.nodes) == 1
    assert graph.edges == []


def test_invalid_expression_marked_invalid():
    graph = build_graph([("not-a-cron", "bad")])
    assert len(graph.nodes) == 1
    assert graph.nodes[0].valid is False
    assert graph.nodes[0].parse_error is not None


def test_no_overlap_no_edges():
    # minute 0 vs minute 30 — no overlap
    graph = build_graph([("0 * * * *", "a"), ("30 * * * *", "b")])
    assert graph.edges == []


def test_identical_expressions_produce_overlap_edge():
    graph = build_graph([("0 9 * * 1", "a"), ("0 9 * * 1", "b")])
    assert len(graph.edges) == 1
    assert graph.edges[0].kind == "overlap"


def test_subset_relationship_detected():
    # "0 9 * * 1" runs Mon 09:00; "0 9 * * *" runs every day 09:00 — first is subset
    graph = build_graph([("0 9 * * 1", "mon"), ("0 9 * * *", "daily")])
    subset_edges = [e for e in graph.edges if e.kind == "subset"]
    assert len(subset_edges) == 1
    assert "mon" in subset_edges[0].source or "mon" in subset_edges[0].description


def test_overlap_between_two_partial_expressions():
    # Both run on Mon and Tue at 9:00, but each also covers other days
    graph = build_graph([("0 9 * * 1,2", "a"), ("0 9 * * 2,3", "b")])
    overlap_edges = [e for e in graph.edges if e.kind == "overlap"]
    assert len(overlap_edges) == 1


def test_invalid_node_skipped_for_edges():
    graph = build_graph([("bad expr", "x"), ("* * * * *", "all")])
    assert len(graph.nodes) == 2
    assert graph.edges == []


def test_format_graph_contains_nodes_section():
    graph = build_graph([("0 9 * * *", "daily")])
    output = format_graph(graph)
    assert "Nodes:" in output
    assert "daily" in output
    assert "valid" in output


def test_format_graph_shows_no_relationships_when_none():
    graph = build_graph([("0 9 * * *", "a")])
    output = format_graph(graph)
    assert "No overlaps" in output


def test_format_graph_shows_edge():
    graph = build_graph([("0 9 * * 1", "mon"), ("0 9 * * *", "daily")])
    output = format_graph(graph)
    assert "Relationships:" in output
    assert any(e.kind in ("overlap", "subset") for e in graph.edges)


def test_format_summary_counts():
    graph = build_graph([("0 9 * * 1", "mon"), ("0 9 * * *", "daily"), ("bad", None)])
    summary = format_summary(graph)
    assert "3 expression(s)" in summary
    assert "1 invalid" in summary
