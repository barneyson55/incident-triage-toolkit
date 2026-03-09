# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- ITK-019 completed (incident evidence semantics are now shared across `summary`, `timeline`, and `runbook`):
  - `triage_toolkit/cli.py::_build_incident_summary()` now reuses the shared evidence helpers instead of counting only `level == "ERROR"` and grouping raw messages independently.
  - `triage_toolkit/evidence.py` now exposes shared `top_error_signatures()` output shaping for JSON and makes signature/component tie-breaks explicit and deterministic (`count DESC`, then earliest evidence timestamp, then name/signature text).
  - `summary.error_count` now matches markdown evidence classification for `ERROR`, `CRITICAL`, `FATAL`, and lower-level messages containing `error`.
  - `summary.top_error_signatures`, timeline `Notable Errors`, and runbook evidence/symptom sections now all use the same normalized signature rules (lowercase, `cid=<id>`, digits -> `#`).
  - `README.md` now documents the canonical evidence-classification and signature-ordering rules.
  - `tests/test_cli.py`, `tests/test_timeline.py`, and `tests/test_runbook.py` now lock parity coverage for `CRITICAL`, `FATAL`, and message-hint evidence.
- Why:
  - The repo was undermining operator trust by letting JSON and markdown disagree about the same incident slice. This closes that semantic gap without changing the CLI surface.
- Risks / follow-ups:
  - Successful parsed events still lack source provenance (source path / line number), which limits how traceable the normalized evidence snippets can be in multi-input incidents.
  - Dropped-line diagnostics and evidence excerpts still need deterministic redaction controls before safe-sharing is strong enough by default.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and (critical or fatal or error)"` ✅
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "critical or fatal or error"` ✅
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "critical or fatal or error"` ✅
  - `make lint` ✅
  - `make test` ✅ (91 passed)

## Next
- Start ITK-020 by preserving source provenance for successful parsed events and rendered evidence so operators can trace normalized evidence back to the original file/stdin source and line.
