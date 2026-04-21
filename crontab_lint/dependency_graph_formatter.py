"""Formatter for DependencyGraph output."""
from __future__ import annotations

from .dependency_graph import DependencyGraph


def format_node(node) -> str:
    status = "valid" if node.valid else f"INVALID ({node.parse_error})"
    label = f" [{node.label}]" if node.label else ""
    return f"  {node.expression}{label}  ({status})"


def format_edge(edge) -> str:
    icon = "⊂" if edge.kind == "subset" else "↔"
    return f"  {icon}  {edge.description}"


def format_graph(graph: DependencyGraph) -> str:
    lines = ["Dependency Graph", "================"]

    lines.append("\nNodes:")
    if graph.nodes:
        for node in graph.nodes:
            lines.append(format_node(node))
    else:
        lines.append("  (none)")

    lines.append("\nRelationships:")
    if graph.edges:
        for edge in graph.edges:
            lines.append(format_edge(edge))
    else:
        lines.append("  No overlaps or subset relationships detected.")

    return "\n".join(lines)


def format_summary(graph: DependencyGraph) -> str:
    n_nodes = len(graph.nodes)
    n_invalid = sum(1 for n in graph.nodes if not n.valid)
    n_edges = len(graph.edges)
    n_overlaps = sum(1 for e in graph.edges if e.kind == "overlap")
    n_subsets = sum(1 for e in graph.edges if e.kind == "subset")
    return (
        f"{n_nodes} expression(s) | {n_invalid} invalid | "
        f"{n_overlaps} overlap(s) | {n_subsets} subset relationship(s)"
    )
