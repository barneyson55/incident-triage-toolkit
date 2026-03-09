# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Partial ITK-016 milestone (deterministic incident-slicing filters, summary-first):
  - `triage_toolkit/cli.py`: added repeated `triage summary` filters for `--component`, `--level`, and `--correlation-id`.
  - Filter behavior is deterministic: repeated same-field flags widen with OR, different fields combine with AND, and filtered event ordering stays inherited from the existing deterministic merge order.
  - Strict parse gates still evaluate raw ingestion quality before filtering, so filtered summaries cannot mask parse failures.
  - `tests/test_cli.py`: added regression coverage for repeated filters, empty filtered slices, and strict/raw-ingestion behavior.
  - `README.md`: documented the current filter semantics and explicitly scoped this milestone to `summary` while `timeline`/`runbook` remain pending.
- Why:
  - Operators can now slice noisy incident summaries by component, severity, and correlation ID without ad-hoc shell pipelines.
- Risks / follow-ups:
  - `timeline` and `runbook` still need the same filter surface to fully complete ITK-016.
  - Current component and correlation-ID matching is exact-string based; if future log normalization changes, the filter contract should be revisited explicitly.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and filter"` ✅
  - `make test` ✅

## Next
- Continue ITK-016 by extending the same deterministic filter surface to `timeline` and `runbook`.
