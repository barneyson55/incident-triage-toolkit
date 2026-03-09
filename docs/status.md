# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- ITK-017 completed (runbook output is now evidence-driven instead of mostly boilerplate):
  - Added shared evidence helpers in `triage_toolkit/evidence.py` for ordered event handling, error classification, normalized signatures, component ranking, and representative correlation IDs.
  - `triage_toolkit/runbook.py` now renders a deterministic evidence snapshot with incident window, first/last observed timestamps, evidence-event counts, top error signatures, suspected components with counts, representative correlation IDs, and 1-3 representative failures chosen as the earliest occurrence for each top signature.
  - Empty or filter-miss runbooks now use an explicit no-evidence template instead of generic filler.
  - `triage_toolkit/timeline.py` now reuses the shared evidence helpers so markdown evidence logic does not fork between timeline and runbook.
  - `tests/test_runbook.py`, `tests/test_cli.py`, and `tests/fixtures/golden/runbook_output.md` were updated to lock the richer markdown contract and representative-failure selection.
  - `README.md` documents the upgraded runbook evidence structure and how filtered slices affect the evidence sections.
- Why:
  - The biggest remaining operator-facing gap was that the runbook read like a template instead of a strong handoff artifact. The richer evidence snapshot makes the markdown output materially more useful without changing the CLI surface.
- Risks / follow-ups:
  - `triage summary` still uses narrower error semantics than timeline/runbook, so JSON and markdown outputs can still disagree about what counts as incident evidence.
  - Successful parsed events still lack source provenance (source path / line number), which limits how traceable the new evidence snippets can be in multi-input incidents.
  - Richer evidence excerpts increase safe-sharing pressure; deterministic redaction is still a follow-up item.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "golden or evidence or example or signature"` ✅
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "runbook and (golden or filter or strict)"` ✅
  - `make lint` ✅
  - `make test` ✅ (87 passed)

## Next
- Start ITK-019 by unifying incident evidence semantics across `summary`, `timeline`, and `runbook` so JSON and markdown outputs stop disagreeing about the same incident.
