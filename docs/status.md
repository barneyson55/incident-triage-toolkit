# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Completed ITK-008 (expand regression matrix + raise CI confidence margin):
  - Added CLI failure-path coverage for directory input, UTF-8 decode failures, unreadable/generic read errors, output write failures, and non-stdout write success paths.
  - Added parser dropped-reason edge coverage (`json_not_object`, `invalid_timestamp` text path, `unknown` fallback) and wrapper-path tests.
  - Added utils timestamp edge coverage (invalid, naive, and offset variants with UTC normalization).
  - Raised CI coverage floor from 85 → 88 (`.github/workflows/ci.yml`).
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "missing_file or directory or utf8 or write or strict or drop_ratio"` ✅
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "invalid_json or json_not_object or missing_timestamp or invalid_timestamp or offset or timezone"` ✅
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=88` ✅ (98.24%)
  - `make lint && make test` ✅ (47 passed)

## Next
- ITK-010 (P1): Preserve timezone provenance while keeping UTC as canonical output.
