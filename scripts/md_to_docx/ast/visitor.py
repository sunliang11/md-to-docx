"""AST visitor utilities."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


class NodeVisitor:
    def visit(self, node: object) -> None:
        method = f"visit_{type(node).__name__}"
        visitor = getattr(self, method, self.generic_visit)
        visitor(node)

    def generic_visit(self, node: object) -> None:
        for field_name in getattr(node, "__dataclass_fields__", {}):
            value = getattr(node, field_name)
            if isinstance(value, tuple):
                for item in value:
                    if hasattr(item, "__dataclass_fields__"):
                        self.visit(item)
            elif hasattr(value, "__dataclass_fields__"):
                self.visit(value)


class TextCollector(NodeVisitor):
    def __init__(self) -> None:
        self.texts: list[str] = []

    def visit_Text(self, node: n.Text) -> None:
        self.texts.append(node.value)
