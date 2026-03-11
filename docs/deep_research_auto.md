Generated: 2026-03-11 19:03 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `README.md`
- `triage_toolkit/{cli.py,evidence.py,models.py,parser.py,runbook.py,timeline.py}`
- `tests/{test_cli.py,test_main.py,test_parser.py,test_runbook.py,test_timeline.py,test_utils.py}`
- `tests/fixtures/golden/{parse_output.json,timeline_output.md,runbook_output.md,mixed_input.log}`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`106 passed`)

## Live architecture snapshot
1. **The shipping product is in a contract-hardening phase, not a feature-gap phase**
   - Core CLI surfaces already exist for `parse`, `summary`, `timeline`, and `runbook`.
   - Current docs and tests show recent work landed around deterministic ordering, source provenance, source-ranked evidence, and redaction.
   - The highest-value next work is therefore concentrated on locking contracts and localizing regressions faster.

2. **`triage summary` is now a first-class automation API but still lacks a dedicated golden suite**
   - `triage_toolkit/cli.py` emits `SUMMARY_SCHEMA_VERSION = "1.1.0"` and includes `incident_window`, `top_components`, `top_error_signatures`, `evidence_by_source`, `correlation_id_coverage`, and `parse_summary`.
   - The repo already carries dedicated golden fixtures for parse/timeline/runbook, but there is no matching `summary` fixture module yet.
   - The current summary behavior is tested mainly inside `tests/test_cli.py`, which is good coverage but not the clearest review surface for contract drift.
   - Conclusion: a dedicated `summary` contract/golden suite is the highest-leverage next item.

3. **Shared evidence logic has become a critical dependency surface**
   - `triage_toolkit/evidence.py` now provides shared ordering and evidence ranking used by summary, timeline, and runbook.
   - `order_events(...)` now carries the explicit tie-break path (`timestamp`, source-order/path fallback, line number, original iterable position), which is exactly the kind of helper behavior that should have direct unit coverage.
   - Today most regressions would still be discovered indirectly through broader CLI/timeline/runbook tests.
   - Conclusion: helper-level tests in `tests/test_evidence.py` are the next-best payoff after summary contract locking.

4. **Shared CLI plumbing is another multi-surface risk concentration point**
   - `triage_toolkit/cli.py` centralizes parse-summary merging, bounded dropped-line diagnostics carry-forward, strict parse gates, and reusable filter semantics.
   - Those rules affect `summary`, `timeline`, and `runbook`, but most current protection remains command-level.
   - A smaller helper-focused test module would make regressions easier to localize without replacing the broader CLI tests.
   - Conclusion: direct tests for CLI helpers are the right third item once summary and evidence hardening are queued.

## Roadmap decisions derived from the current repo

### P1 — ITK-024: Add dedicated golden/contract coverage for summary JSON
**Why now:** `summary` is a versioned machine-readable surface and the only major output contract that still lacks its own dedicated golden/contract module.

### P1 — ITK-025: Add direct unit coverage for shared evidence and ranking helpers
**Why next:** the repo now depends on `evidence.py` for several surfaces at once, so helper-level regressions should fail closer to the source.

### P2 — ITK-026: Add direct unit coverage for shared CLI ingestion/filter/strict-gate helpers
**Why after that:** CLI helper logic is now important enough to merit smaller focused tests, but the immediate leverage is still better on summary contract locking and evidence-helper coverage.

## Explicitly de-prioritized in this pass
- New parser-format expansion: no current repo evidence says new formats outrank contract/test hardening.
- Fresh feature work on timeline/runbook output shape: the recent priority items for those surfaces are already complete.
- Reopening provenance or redaction as top-level roadmap items: both are already shipped and covered enough to move down unless new regressions appear.

## Risks / blockers to monitor
- ITK-024 should lock semantic contract shape/content without overpromising irrelevant JSON key ordering details.
- ITK-025 must preserve the documented deterministic ordering contract, especially for same-timestamp events with/without explicit source metadata.
- ITK-026 should keep helper tests tied to public CLI behavior, not to brittle incidental implementation details.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-024 — dedicated summary JSON golden/contract coverage
2. ITK-025 — direct evidence/ranking helper unit coverage
3. ITK-026 — direct CLI ingestion/filter/strict-gate helper coverage
