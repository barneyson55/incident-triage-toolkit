# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Completed ITK-010 (preserve timezone provenance while keeping UTC canonical output):
  - `triage_toolkit/models.py`: added additive event fields `source_timestamp` and `source_offset` to `LogEvent.to_dict()`.
  - `triage_toolkit/parser.py`: captured deterministic timestamp provenance for both JSON and text ingestion paths while keeping `timestamp` UTC-normalized.
  - `tests/test_parser.py` and `tests/test_cli.py`: added regression assertions for provenance fields across offset, `Z`, and naive timestamp inputs.
  - `README.md`: documented parse-event schema delta and backward-compatibility (additive keys, UTC-first unchanged).
- Why:
  - Downstream automation can now correlate original source timestamp/offset without giving up deterministic UTC ordering.
- Risks / follow-ups:
  - `source_offset` is `null` for naive timestamps (no explicit offset in source); consumers should not treat `null` as UTC certainty.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "provenance or source_offset or source_timestamp"` ✅
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "parse and provenance and timezone"` ✅
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "utc"` ✅
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "utc"` ✅
  - `make lint && make test` ✅ (50 passed)

## Next
- ITK-011 (P1): Version and lock the parse JSON contract before further output expansion.
