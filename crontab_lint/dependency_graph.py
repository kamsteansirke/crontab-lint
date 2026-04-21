"""Dependency graph: detect ordering/overlap relationships between cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .parser import parse, ParseError
from .conflict_detector import _parse_field_values, _expressions_overlap


@dataclass
class GraphNode:
    expression: str
    label: Optional[str] = None
    valid: bool = True
    parse_error: Optional[str] = None


@dataclass
class GraphEdge:
    source: str
    target: str
    kind: str  # 'overlap' | 'subset'
    description: str


@dataclass
class DependencyGraph:
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)


def _is_subset(a_vals: set, b_vals: set) -> bool:
    """Return True if a_vals is a proper subset of b_vals."""
    return a_vals < b_vals


def _field_sets(expr_str: str):
    """Parse expression and return per-field value sets, or None on error."""
    try:
        expr = parse(expr_str)
    except ParseError:
        return None
    fields = [expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week]
    ranges = [range(60), range(24), range(1, 32), range(1, 13), range(0, 8)]
    return [_parse_field_values(f, r) for f, r in zip(fields, ranges)]


def build_graph(expressions: List[Tuple[str, Optional[str]]]) -> DependencyGraph:
    """Build a dependency graph from a list of (expression, label) tuples."""
    graph = DependencyGraph()
    parsed_sets = []

    for expr_str, label in expressions:
        try:
            parse(expr_str)
            sets = _field_sets(expr_str)
            graph.nodes.append(GraphNode(expression=expr_str, label=label, valid=True))
            parsed_sets.append(sets)
        except ParseError as e:
            graph.nodes.append(GraphNode(expression=expr_str, label=label, valid=False, parse_error=str(e)))
            parsed_sets.append(None)

    n = len(graph.nodes)
    for i in range(n):
        for j in range(i + 1, n):
            a_sets = parsed_sets[i]
            b_sets = parsed_sets[j]
            if a_sets is None or b_sets is None:
                continue

            overlaps = [bool(a & b) for a, b in zip(a_sets, b_sets)]
            if not all(overlaps):
                continue

            a_sub_b = all(_is_subset(a, b) or a == b for a, b in zip(a_sets, b_sets)) and any(
                _is_subset(a, b) for a, b in zip(a_sets, b_sets)
            )
            b_sub_a = all(_is_subset(b, a) or a == b for a, b in zip(a_sets, b_sets)) and any(
                _is_subset(b, a) for a, b in zip(a_sets, b_sets)
            )

            src = graph.nodes[i].label or graph.nodes[i].expression
            tgt = graph.nodes[j].label or graph.nodes[j].expression

            if a_sub_b:
                graph.edges.append(GraphEdge(src, tgt, "subset", f"{src!r} runs on a subset of times covered by {tgt!r}"))
            elif b_sub_a:
                graph.edges.append(GraphEdge(tgt, src, "subset", f"{tgt!r} runs on a subset of times covered by {src!r}"))
            else:
                graph.edges.append(GraphEdge(src, tgt, "overlap", f"{src!r} and {tgt!r} share overlapping run times"))

    return graph
