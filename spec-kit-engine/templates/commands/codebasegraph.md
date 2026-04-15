---
description: Build a Python codebase dependency graph (imports, functions, classes, reverse dependencies) and produce JSON plus a readable summary.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Run the Codebase Graph Engine for the target repository and return:

1. A structured JSON graph
2. A readable summary (files, edges, parse errors)
3. Optional file-level drill-down requested by the user

## Input Resolution

Interpret user input using this precedence:

1. If user provides `--path <dir>`, use that as target path.
2. Else if user provides a path-like argument, use it.
3. Else default target path to `.` (current project root).

Output resolution:

1. If user provides `--output <file>`, use it.
2. Else default to `.specify/analysis/codebase-graph.json` under the target path.

## Execution Flow

1. Validate target path exists and is a directory.
2. Detect Codebase Graph Engine availability:
   - Preferred: `main.py` and `codebase_graph_engine/` exist in repo root.
   - If not found, stop and output setup commands instead of guessing behavior.
3. Run the engine:
   - `python main.py --path <target> --output <output>`
   - Add `--no-cache` only when user explicitly requests a full rebuild.
4. Confirm output JSON was created.
5. Parse output JSON and summarize:
   - total scanned files
   - total dependency edges
   - parse error count and top parse errors
   - top files by number of dependencies
   - top files by number of dependents
6. If user asks for a specific file, return:
   - direct dependencies
   - dependents
   - functions/classes summary for that file

## Required JSON Shape

Expect and preserve this structure:

```json
{
  "root": "...",
  "graph": {
    "file.py": {
      "imports": ["..."],
      "functions": ["..."],
      "classes": ["..."]
    }
  },
  "reverse_dependencies": {
    "file.py": ["dependent.py"]
  },
  "parse_errors": {
    "bad.py": "Syntax error ..."
  }
}
```

## Error Handling

- If engine files are missing, do not fabricate output.
- If execution fails, include the failing command and stderr summary.
- If JSON parsing fails, report path and parse error clearly.
- If target has no Python files, return an empty graph with explanation.

## Final Output Contract

Always provide:

1. `Target Path`
2. `Output JSON Path`
3. `Summary` (files, edges, parse errors)
4. `Next actions` (for example, inspect a file, re-run with --no-cache)
