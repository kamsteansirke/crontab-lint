"""Annotate crontab expressions with inline comments."""
from dataclasses import dataclass
from typing import List, Optional
from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain


@dataclass
class AnnotatedLine:
    original: str
    annotation: Optional[str]
    is_comment: bool
    is_blank: bool
    is_valid: bool


def annotate_line(line: str) -> AnnotatedLine:
    stripped = line.strip()
    if not stripped:
        return AnnotatedLine(line, None, False, True, True)
    if stripped.startswith("#"):
        return AnnotatedLine(line, None, True, False, True)
    try:
        expr = parse(stripped)
        annotation = explain(expr)
        return AnnotatedLine(line, annotation, False, False, True)
    except ParseError as e:
        return AnnotatedLine(line, f"ERROR: {e}", False, False, False)


def annotate(lines: List[str]) -> List[AnnotatedLine]:
    return [annotate_line(line) for line in lines]


def format_annotated(annotated: List[AnnotatedLine], comment_char: str = "#") -> str:
    result = []
    for entry in annotated:
        if entry.is_blank:
            result.append(entry.original.rstrip())
        elif entry.is_comment:
            result.append(entry.original.rstrip())
        elif entry.annotation:
            result.append(f"{entry.original.rstrip()}  {comment_char} {entry.annotation}")
        else:
            result.append(entry.original.rstrip())
    return "\n".join(result)
