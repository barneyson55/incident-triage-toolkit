Generated: 2026-03-11 21:20 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `README.md`
- `triage_toolkit/{cli.py,evidence.py,models.py,parser.py,redaction.py,runbook.py,timeline.py,utils.py}`
- `tests/{test_cli.py,test_evidence.py,test_main.py,test_parser.py,test_runbook.py,test_summary_contract.py,test_timeline.py,test_utils.py}`
- `tests/fixtures/golden/{parse_output.json,summary_output_single.json,summary_output_multi.json,summary_output_stdin.json,summary_output_filter_miss.json,timeline_output.md,runbook_output.md,mixed_input.log}`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`118 passed`)

## Live architecture snapshot
1. **The repo is still in a hardening phase, but the center of gravity has shifted**
   - Core CLI surfaces for `parse`, `summary`, `timeline`, and `runbook` are in place and already have strong command-level coverage.
   - `tests/test_evidence.py` now exists, so the previous top gap around `triage_toolkit/evidence.py` has been closed.
   - The next highest leverage is reducing the remaining places where shared behavior only fails through broader CLI tests.

2. **`triage_toolkit/cli.py` is now the most important un-factored test surface**
   - It owns parse-summary aggregation, diagnostics-budget carry-forward, duplicate-stdin rejection, strict parse gates, reusable filters, and the shared write path.
   - Those invariants affect every command, but there is still no dedicated `tests/test_cli_helpers.py` suite.
   - Conclusion: helper-focused CLI coverage should be the first live item.

3. **`triage_toolkit/redaction.py` is still under-protected relative to its risk**
   - Redaction is regex-heavy, order-sensitive, and shared across parse diagnostics plus human-readable timeline/runbook output.
   - Existing tests prove outcomes end-to-end, but there is still no direct `tests/test_redaction.py` locking regex boundaries and replacement order.
   - Conclusion: redaction helper coverage stays immediately behind CLI helpers.

4. **Cross-surface parity is the next most valuable regression net**
   - `summary`, `timeline`, and `runbook` all derive from shared evidence/filtering behavior.
   - Today that consistency is protected indirectly by separate assertions in separate test modules.
   - Conclusion: one fixture-driven parity suite would catch subtle drift in counts, signatures, source ranking, or incident-window slicing sooner.

5. **Full redacted outputs are not frozen yet**
   - The repo has golden fixtures for the non-redacted contract surfaces.
   - The redacted paths currently rely on targeted substring assertions rather than full-output golden checks.
   - Conclusion: once redaction helper behavior is locked, redacted golden fixtures become the next clean contract hardening step.

## Roadmap decisions derived from the current repo

### P1 — ITK-026: Add direct unit coverage for shared CLI ingestion/filter/strict-gate/write helpers
**Why now:** this is the densest remaining shared correctness surface and still lacks focused helper tests.

### P1 — ITK-027: Add direct unit coverage for shared redaction helpers and placeholder stability
**Why next:** regex-heavy redaction can drift silently, and direct helper tests will fail closer to the source than current end-to-end coverage.

### P2 — ITK-028: Add a fixture-driven parity suite for `summary`, `timeline`, and `runbook`
**Why after that:** shared-slice drift across surfaces is now more likely than core feature gaps.

### P2 — ITK-029: Tighten parser helper coverage for provenance extraction, diagnostics builders, and source-order propagation
**Why now but slightly later:** parser coverage is already decent, so this is meaningful hardening but not the very first gap anymore.

### P3 — ITK-030: Add full redacted golden fixtures for parse/timeline/runbook outputs
**Why later:** this is contract hardening, but it builds best on top of the direct redaction-helper suite first.

## Explicitly de-prioritized in this pass
- New parser-format expansion: nothing in the current repo evidence says new format support now outranks hardening shared correctness and contract surfaces.
- New output features for `timeline` or `runbook`: those surfaces already have dedicated tests and recent deterministic/evidence improvements.
- Reopening evidence-helper work as the top item: `tests/test_evidence.py` exists and `docs/status.md` records that work as complete.

## Risks / blockers to monitor
- ITK-026 should lock public invariants without making helper tests brittle against harmless refactors.
- ITK-027 needs to preserve current redaction boundaries while leaving room for future additive placeholder coverage.
- ITK-028 must compare equivalent semantics across JSON and markdown outputs without overfitting to presentation noise.
- ITK-029 should focus on provenance/diagnostics/source-order behavior, not re-test every parser path already covered elsewhere.
- ITK-030 will be maintenance-heavy if fixtures are too large; keep them compact and purpose-built.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-026 — direct CLI helper unit coverage
2. ITK-027 — direct redaction helper and placeholder-stability coverage
3. ITK-028 — cross-surface parity tests for shared filtered incident slices
4. ITK-029 — parser helper coverage for provenance/diagnostics/source-order behavior
5. ITK-030 — redacted golden-output contract coverage
