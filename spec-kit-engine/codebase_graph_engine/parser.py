"""AST parsing utilities for Python source files."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ImportRef:
    """Structured representation of an import statement."""

    kind: str  # "import" or "from"
    module: str | None
    names: list[str]
    level: int = 0


@dataclass(slots=True)
class ParsedFile:
    """AST-derived metadata for a Python file."""

    path: Path
    module: str
    imports: list[ImportRef]
    functions: list[str]
    classes: list[str]
    parse_error: str | None = None


class _SymbolVisitor(ast.NodeVisitor):
    """Collect import/function/class metadata from a Python module AST."""

    def __init__(self) -> None:
        self.imports: list[ImportRef] = []
        self.functions: list[str] = []
        self.classes: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        names = [alias.name for alias in node.names]
        self.imports.append(ImportRef(kind="import", module=None, names=names, level=0))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        names = [alias.name for alias in node.names]
        self.imports.append(
            ImportRef(
                kind="from",
                module=node.module,
                names=names,
                level=node.level,
            )
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self.functions.append(node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self.functions.append(node.name)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self.classes.append(node.name)


def module_name_from_path(file_path: Path, root_path: Path) -> str:
    """Convert a source file path to a dotted module name."""
    relative = file_path.relative_to(root_path).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_python_file(file_path: Path, root_path: Path) -> ParsedFile:
    """Parse one Python source file and extract symbols and imports."""
    module = module_name_from_path(file_path, root_path)

    try:
        source = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = file_path.read_text(encoding="latin-1")
    except OSError as exc:
        return ParsedFile(
            path=file_path,
            module=module,
            imports=[],
            functions=[],
            classes=[],
            parse_error=f"I/O error: {exc}",
        )

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return ParsedFile(
            path=file_path,
            module=module,
            imports=[],
            functions=[],
            classes=[],
            parse_error=f"Syntax error: {exc.msg} (line {exc.lineno})",
        )

    visitor = _SymbolVisitor()
    visitor.visit(tree)

    return ParsedFile(
        path=file_path,
        module=module,
        imports=visitor.imports,
        functions=sorted(set(visitor.functions)),
        classes=sorted(set(visitor.classes)),
        parse_error=None,
    )
