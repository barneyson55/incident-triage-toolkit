# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- ITK-020 completed (successful parsed events and rendered evidence now preserve source provenance):
  - `triage_toolkit/models.py::LogEvent` now carries `source_path` and `line_number`, and the parse JSON schema moved to `1.2.0`.
  - `triage_toolkit/parser.py::parse_lines_with_summary()` now stamps each successful event with its stable source label (`-` for stdin, full path for files) plus original 1-based line number without changing parse gates or merge ordering.
  - `triage_toolkit/timeline.py` now renders a concise `Source` column as `source_path:line_number` for each timeline row.
  - `triage_toolkit/runbook.py` now cites the same provenance in top-signature evidence (`example: ...`) and example-failure bullets.
  - `README.md` and golden fixtures now document/lock the new schema and provenance rendering contract.
- Why:
  - Multi-input incidents are much more auditable when normalized events can be traced back to the exact file/stdin source and original line.
- Risks / follow-ups:
  - Dropped-line diagnostics and evidence excerpts still need deterministic redaction controls before safe-sharing is strong enough by default.
  - The next useful upgrade is per-source evidence concentration so operators can see which source dominates the incident slice.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "source and line"` ✅
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "parse and provenance"` ✅
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "provenance"` ✅
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "provenance"` ✅
  - `make lint` ✅
  - `make test` ✅ (94 passed)

## Next
- Start ITK-021 by adding deterministic redaction controls for diagnostics and evidence surfaces.
