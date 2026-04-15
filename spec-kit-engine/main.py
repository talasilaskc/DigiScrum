"""CLI entrypoint for the Codebase Graph Engine.

Example:
    python main.py --path ./repo
"""

from __future__ import annotations

import argparse
from pathlib import Path

from codebase_graph_engine import build_graph


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build a Python codebase dependency graph")
    parser.add_argument("--path", required=True, help="Root path of the repository")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache and rebuild the graph from source files",
    )
    parser.add_argument(
        "--output",
        help="Optional output JSON file path",
    )
    return parser.parse_args()


def main() -> int:
    """Run CLI command."""
    args = parse_args()

    graph = build_graph(Path(args.path), use_cache=not args.no_cache)
    graph.print_summary()

    json_output = graph.to_json(indent=2)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_output, encoding="utf-8")
        print(f"Wrote graph JSON to: {out_path}")
    else:
        print("\nGraph JSON:")
        print(json_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
