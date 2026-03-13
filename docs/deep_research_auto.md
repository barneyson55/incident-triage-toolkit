Generated: 2026-03-13 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `README.md`
- `docs/AI_EDIT_POLICY.md`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- live file-existence checks for the key docs requested in this pass
- live repo status via `git status --short --branch`
- focused symbol/test searches across `tests/`, `triage_toolkit/parser.py`, and `triage_toolkit/cli.py`
- live verification via `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry (`## main...origin/main`)
- `docs/user_todo.md` exists and has no open checkbox items
- live coverage check:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`183 passed`)
  - total coverage: `99%`
  - uncovered lines are now limited to a few thin branches in `triage_toolkit/cli.py` and `triage_toolkit/parser.py`
- focused repo search confirmed:
  - direct parser alias coverage now exists in `tests/test_parser.py`
  - no focused timeline/runbook tests currently lock pipe escaping or newline flattening
  - no direct tests currently lock `_read_stdin_lines()` fallback-without-buffer, `_read_events_for_parse([])`, `parse_file(...)`, or `main()`

## Priority conclusions
1. **ITK-037** — add a compact end-to-end CLI contract fixture for alias-shaped JSON logs
2. **ITK-034** — add focused markdown formatting edge coverage for timeline/runbook
3. **ITK-036** — close the remaining thin wrapper/helper branch gaps

## What changed vs the previous ordering
Previous refresh logic still treated **ITK-035** as the top open item.
That is now stale because `docs/status.md` and `tests/test_parser.py` show **ITK-035 is completed**.

Refreshed open queue:
1. **ITK-037** moves to the top because the remaining heterogeneous-ingestion risk now lives at the public CLI contract layer, not the parser seam.
2. **ITK-034** stays ahead of wrapper cleanup because malformed markdown affects operator handoffs directly.
3. **ITK-036** remains last because the uncovered lines are small wrapper branches rather than core product semantics.

## Risks / blockers to watch
- **Task overlap risk:** keep ITK-037 CLI-contract-focused; do not re-implement parser-local assertions already covered by ITK-035.
- **Golden-test sprawl:** ITK-037 and ITK-034 should prefer compact fixtures and narrow assertions over broad golden churn.
- **Coverage vanity risk:** ITK-036 should remain cleanup work after the higher-value contract gaps are locked.
- **No blocker file escalation needed:** `docs/critical_todo.md` is present and contains no non-negotiable issues.

## Why this refresh was needed
The queue needed to catch up with the repo’s actual state:
- parser alias handling is now directly covered
- the highest-value remaining gap is end-to-end CLI proof for alias-heavy inputs
- the next user-visible gap is markdown rendering edge coverage
- the final cleanup is thin wrapper branch coverage
