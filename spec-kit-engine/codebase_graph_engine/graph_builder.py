"""Dependency graph construction and query APIs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .parser import ImportRef, ParsedFile, module_name_from_path, parse_python_file
from .scanner import scan_python_files

_CACHE_FILE = ".codebase_graph_cache.json"
_ACTIVE_GRAPH: CodebaseGraph | None = None


@dataclass(slots=True)
class FileNode:
    """Per-file graph metadata."""

    imports: list[str]
    functions: list[str]
    classes: list[str]


@dataclass(slots=True)
class CodebaseGraph:
    """In-memory dependency graph with query helpers."""

    root_path: Path
    nodes: dict[str, FileNode]
    reverse_dependencies: dict[str, list[str]]
    parse_errors: dict[str, str]

    def get_dependencies(self, file_name: str) -> list[str]:
        """Return direct file dependencies for *file_name*."""
        node = self.nodes.get(file_name)
        return list(node.imports) if node else []

    def get_dependents(self, file_name: str) -> list[str]:
        """Return direct reverse dependencies for *file_name*."""
        return list(self.reverse_dependencies.get(file_name, []))

    def get_file_summary(self, file_name: str) -> dict[str, Any]:
        """Return merged metadata for one file."""
        node = self.nodes.get(file_name)
        if not node:
            return {}
        return {
            "imports": list(node.imports),
            "functions": list(node.functions),
            "classes": list(node.classes),
            "dependents": self.get_dependents(file_name),
            "parse_error": self.parse_errors.get(file_name),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to a JSON-safe dictionary."""
        graph_dict = {
            file_name: {
                "imports": node.imports,
                "functions": node.functions,
                "classes": node.classes,
            }
            for file_name, node in sorted(self.nodes.items())
        }
        return {
            "root": self.root_path.as_posix(),
            "graph": graph_dict,
            "reverse_dependencies": {
                key: sorted(value) for key, value in sorted(self.reverse_dependencies.items())
            },
            "parse_errors": dict(sorted(self.parse_errors.items())),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize graph to JSON."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def print_summary(self) -> None:
        """Print a readable graph summary."""
        total_edges = sum(len(node.imports) for node in self.nodes.values())
        print(f"Scanned files: {len(self.nodes)}")
        print(f"Dependency edges: {total_edges}")
        if self.parse_errors:
            print(f"Parse errors: {len(self.parse_errors)}")
            for file_name, err in sorted(self.parse_errors.items()):
                print(f"  - {file_name}: {err}")


def _relative_path(path: Path, root_path: Path) -> str:
    return path.relative_to(root_path).as_posix()


def _build_module_index(files: list[Path], root_path: Path) -> dict[str, str]:
    """Map dotted module names to project-relative Python file paths."""
    index: dict[str, str] = {}
    for file_path in files:
        module_name = module_name_from_path(file_path, root_path)
        rel = _relative_path(file_path, root_path)
        if module_name:
            index[module_name] = rel
        if file_path.stem != "__init__":
            index[file_path.stem] = index.get(file_path.stem, rel)
    return index


def _current_package(module_name: str, file_path: Path) -> str:
    if file_path.name == "__init__.py":
        return module_name
    if "." in module_name:
        return module_name.rsplit(".", 1)[0]
    return ""


def _resolve_relative_base(module_name: str, level: int, file_path: Path) -> str:
    package = _current_package(module_name, file_path)
    if level <= 0:
        return package

    parts = package.split(".") if package else []
    ascend = max(level - 1, 0)
    if ascend >= len(parts):
        return ""
    if ascend == 0:
        return package
    return ".".join(parts[:-ascend])


def _candidate_modules(import_ref: ImportRef, parsed: ParsedFile) -> list[str]:
    candidates: list[str] = []

    if import_ref.kind == "import":
        candidates.extend(import_ref.names)
        return candidates

    base = import_ref.module or ""
    if import_ref.level > 0:
        rel_base = _resolve_relative_base(parsed.module, import_ref.level, parsed.path)
        base = f"{rel_base}.{base}".strip(".") if base else rel_base

    if base:
        candidates.append(base)

    for name in import_ref.names:
        if name == "*":
            continue
        if base:
            candidates.append(f"{base}.{name}")
        else:
            candidates.append(name)

    return candidates


def _resolve_module_to_file(module_name: str, module_index: dict[str, str]) -> str | None:
    """Resolve an import module string to a project file if possible."""
    if module_name in module_index:
        return module_index[module_name]

    parts = module_name.split(".")
    for i in range(len(parts) - 1, 0, -1):
        candidate = ".".join(parts[:i])
        if candidate in module_index:
            return module_index[candidate]

    return None


def _signature(files: list[Path], root_path: Path) -> dict[str, dict[str, int]]:
    sig: dict[str, dict[str, int]] = {}
    for path in files:
        stat = path.stat()
        sig[_relative_path(path, root_path)] = {
            "mtime_ns": stat.st_mtime_ns,
            "size": stat.st_size,
        }
    return sig


def _load_cached_graph(cache_path: Path, signature: dict[str, dict[str, int]]) -> dict[str, Any] | None:
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if payload.get("signature") != signature:
        return None

    graph_data = payload.get("graph")
    if not isinstance(graph_data, dict):
        return None
    return graph_data


def _write_cache(cache_path: Path, signature: dict[str, dict[str, int]], graph: CodebaseGraph) -> None:
    payload = {
        "signature": signature,
        "graph": graph.to_dict(),
    }
    try:
        cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        return


def _graph_from_dict(root_path: Path, data: dict[str, Any]) -> CodebaseGraph:
    nodes: dict[str, FileNode] = {}
    for file_name, node_data in data.get("graph", {}).items():
        nodes[file_name] = FileNode(
            imports=list(node_data.get("imports", [])),
            functions=list(node_data.get("functions", [])),
            classes=list(node_data.get("classes", [])),
        )

    reverse = {
        key: list(value)
        for key, value in data.get("reverse_dependencies", {}).items()
        if isinstance(value, list)
    }
    errors = {
        key: value
        for key, value in data.get("parse_errors", {}).items()
        if isinstance(value, str)
    }

    return CodebaseGraph(root_path=root_path, nodes=nodes, reverse_dependencies=reverse, parse_errors=errors)


def build_graph(root_path: str | Path, use_cache: bool = True) -> CodebaseGraph:
    """Build a file dependency graph for Python source under *root_path*."""
    root = Path(root_path).resolve()
    files = scan_python_files(root)

    cache_path = root / _CACHE_FILE
    sig = _signature(files, root)

    global _ACTIVE_GRAPH

    if use_cache and cache_path.exists():
        cached = _load_cached_graph(cache_path, sig)
        if cached is not None:
            _ACTIVE_GRAPH = _graph_from_dict(root, cached)
            return _ACTIVE_GRAPH

    module_index = _build_module_index(files, root)
    nodes: dict[str, FileNode] = {}
    reverse: dict[str, set[str]] = {}
    errors: dict[str, str] = {}

    for file_path in files:
        parsed = parse_python_file(file_path, root)
        rel = _relative_path(file_path, root)

        if parsed.parse_error:
            errors[rel] = parsed.parse_error

        imports: set[str] = set()
        for import_ref in parsed.imports:
            for module_name in _candidate_modules(import_ref, parsed):
                resolved = _resolve_module_to_file(module_name, module_index)
                if resolved and resolved != rel:
                    imports.add(resolved)

        resolved_imports = sorted(imports)
        nodes[rel] = FileNode(
            imports=resolved_imports,
            functions=parsed.functions,
            classes=parsed.classes,
        )

        for dep in resolved_imports:
            reverse.setdefault(dep, set()).add(rel)

    reverse_dependencies = {
        file_name: sorted(list(dependents))
        for file_name, dependents in sorted(reverse.items())
    }

    graph = CodebaseGraph(
        root_path=root,
        nodes=nodes,
        reverse_dependencies=reverse_dependencies,
        parse_errors=errors,
    )

    if use_cache:
        _write_cache(cache_path, sig, graph)

    _ACTIVE_GRAPH = graph
    return graph


def _resolve_graph(graph: CodebaseGraph | None = None) -> CodebaseGraph:
    selected = graph or _ACTIVE_GRAPH
    if selected is None:
        raise RuntimeError("No active graph available. Call build_graph(root_path) first.")
    return selected


def get_dependencies(file_name: str, graph: CodebaseGraph | None = None) -> list[str]:
    """Return direct dependencies for *file_name*.

    If *graph* is omitted, the most recently built active graph is used.
    """
    return _resolve_graph(graph).get_dependencies(file_name)


def get_dependents(file_name: str, graph: CodebaseGraph | None = None) -> list[str]:
    """Return direct dependents for *file_name*.

    If *graph* is omitted, the most recently built active graph is used.
    """
    return _resolve_graph(graph).get_dependents(file_name)


def get_file_summary(file_name: str, graph: CodebaseGraph | None = None) -> dict[str, Any]:
    """Return a metadata summary for *file_name*.

    If *graph* is omitted, the most recently built active graph is used.
    """
    return _resolve_graph(graph).get_file_summary(file_name)
