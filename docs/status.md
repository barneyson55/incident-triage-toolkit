# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Completed ITK-004 (parse-quality gate to prevent silent data loss):
  - Updated `triage_toolkit/parser.py` to add deterministic parse-quality telemetry:
    - `total_lines`, `parsed_lines`, `dropped_lines`, `drop_ratio`
    - dropped-reason buckets (`blank_line`, `invalid_json`, `json_not_object`, `missing_timestamp`, `invalid_timestamp`, `unrecognized_text`)
    - new helpers: `parse_line_with_reason`, `parse_lines_with_summary`, `parse_file_with_summary`
  - Updated `triage_toolkit/cli.py`:
    - `triage parse --strict`
    - `triage parse --max-drop-ratio <0..1>`
    - strict mode exits non-zero when `parsed_lines == 0` or drop ratio exceeds threshold
    - parse output now includes deterministic `parse_summary` alongside `events`
  - Expanded tests:
    - `tests/test_parser.py` for stats + dropped reasons
    - `tests/test_cli.py` for strict-mode and drop-ratio gate behavior
- Why:
  - Prevents silent data loss and makes parse quality visible + enforceable in automation.
- Risks / follow-ups:
  - Parse command output shape now includes `{ "events": [...], "parse_summary": {...} }`; downstream consumers expecting a bare list should adjust.
- Local verification executed:
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "stats or dropped"` ✅
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "strict or drop_ratio"` ✅
  - `make lint` ✅
  - `make test` ✅ (12 passed)

## Next
- ITK-006 (P0): Normalize outputs to UTC and accept offset-heavy text logs.
