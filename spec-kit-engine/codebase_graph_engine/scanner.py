"""Filesystem scanning utilities for the Codebase Graph Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

_DEFAULT_IGNORED = {"venv", ".venv", "__pycache__"}


def _is_hidden(path: Path) -> bool:
    """Return True when any path segment is hidden (starts with '.')."""
    return any(part.startswith(".") for part in path.parts)


def scan_python_files(
    root_path: Path,
    ignored_dirs: Iterable[str] | None = None,
) -> list[Path]:
    """Recursively scan for Python files under *root_path*.

    Hidden folders, virtual environments, and ``__pycache__`` directories are
    skipped by default.
    """
    if not root_path.exists():
        raise FileNotFoundError(f"Root path does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root_path}")

    ignored = set(ignored_dirs or ()) | _DEFAULT_IGNORED
    python_files: list[Path] = []

    for path in root_path.rglob("*.py"):
        try:
            relative = path.relative_to(root_path)
        except ValueError:
            continue

        if _is_hidden(relative.parent):
            continue

        if any(part in ignored for part in relative.parts):
            continue

        if path.name.startswith("."):
            continue

        python_files.append(path)

    python_files.sort()
    return python_files
