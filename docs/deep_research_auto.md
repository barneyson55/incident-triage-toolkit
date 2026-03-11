Generated: 2026-03-11 23:40 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `README.md`
- repo cleanliness via `git status --short --branch`
- live file-existence checks for the key source/test surfaces referenced by the queue

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` ✅ clean `main...origin/main`
- `docs/status.md` is current through ITK-027 and points to ITK-028 next
- `docs/critical_todo.md` still has no open critical items
- `tests/test_cli_helpers.py` ✅ exists
- `tests/test_evidence.py` ✅ exists
- `tests/test_redaction.py` ✅ exists
- `tests/test_output_parity.py` ❌ missing
- `tests/test_parser.py` ✅ exists
- latest recorded verification in `docs/status.md`: `make test` ✅ (`130 passed`)

## Priority conclusions
1. **ITK-028 should now be the first active item**
   - The prior top gaps around CLI helper coverage and redaction helper coverage are closed.
   - The biggest remaining regression risk is drift between `summary`, `timeline`, and `runbook` when they render the same filtered incident slice.
   - A dedicated parity suite gives the most leverage because it protects shared evidence/filtering semantics across three operator-facing surfaces at once.

2. **ITK-029 stays next, but behind parity**
   - Parser coverage is already decent, so this is hardening rather than a glaring missing net.
   - It still matters because provenance metadata, dropped-line diagnostics, and source-order propagation feed every downstream command.

3. **ITK-030 remains valuable but should stay after the higher-signal shared-behavior tests**
   - Redaction helper behavior is now directly tested.
   - The remaining gap is full-output contract freezing for redacted surfaces, which is important but less urgent than cross-surface semantic parity.

## Resulting active queue
1. ITK-028 — fixture-driven cross-surface parity for `summary` / `timeline` / `runbook`
2. ITK-029 — parser helper coverage for provenance / diagnostics / source-order invariants
3. ITK-030 — redacted golden fixtures for parse diagnostics, timeline, and runbook

## Risks / blockers to watch
- ITK-028 must compare equivalent semantics across JSON and markdown without overfitting to presentation-only text.
- ITK-029 should lock documented behavior, not private implementation trivia.
- ITK-030 can become fixture-maintenance drag if the redacted goldens are too large; keep them compact and purpose-built.

## Why this refresh was needed
The previous deep-research note still reflected the pre-ITK-027 state, which made the active queue look one maintenance pass behind. This refresh brings the background note back in sync with `docs/status.md` and the live test surface.
