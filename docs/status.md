# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Completed ITK-006 (normalize outputs to UTC and accept offset-heavy text logs):
  - Updated `triage_toolkit/utils.py`:
    - all parsed datetimes are now normalized to UTC (`+00:00`) before returning
    - applies to `Z`, `+HH:MM`, `-HH:MM`, and naive timestamps (assumed UTC)
  - Updated `triage_toolkit/parser.py`:
    - text-log timestamp regex now accepts RFC3339 offsets (`+HH:MM`, `-HH:MM`) in addition to `Z`
  - Expanded regression coverage:
    - `tests/test_parser.py`: offset parsing + UTC normalization for text and JSON lines
    - `tests/test_timeline.py`: mixed-offset ordering and rendered UTC timeline output
    - `tests/test_runbook.py`: UTC-normalized "First observed" rendering
    - `tests/test_cli.py`: parse JSON output emits UTC-normalized timestamps
- Why:
  - Removes mixed-timezone ambiguity so parse output, timeline, and runbook all represent a single UTC timeline.
- Risks / follow-ups:
  - UTC normalization now rewrites non-UTC input offsets in emitted output, which may affect downstream expectations if raw offsets were previously relied upon.
- Local verification executed:
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "timezone or offset"` ✅
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "utc or timezone"` ✅
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "utc or timezone"` ✅
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "offset or timezone"` ✅
  - `make lint` ✅
  - `make test` ✅ (17 passed)

## Next
- ITK-005 (P1): Refactor ingestion to stream line-by-line (large-file safe).
