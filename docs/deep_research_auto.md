Generated: 2026-03-11 20:05 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `README.md`
- `triage_toolkit/{cli.py,evidence.py,models.py,parser.py,redaction.py,runbook.py,timeline.py}`
- `tests/{test_cli.py,test_main.py,test_parser.py,test_runbook.py,test_summary_contract.py,test_timeline.py,test_utils.py}`
- `tests/fixtures/golden/{parse_output.json,summary_output_single.json,summary_output_multi.json,summary_output_stdin.json,summary_output_filter_miss.json,timeline_output.md,runbook_output.md,mixed_input.log}`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`111 passed`)

## Live architecture snapshot
1. **The repo is still in a contract-and-helper hardening phase, not a greenfield feature phase**
   - Core CLI surfaces already exist for `parse`, `summary`, `timeline`, and `runbook`.
   - Recent completed work locked summary golden outputs and clarified same-timestamp determinism.
   - The biggest remaining leverage is now in making shared helper regressions fail closer to their source.

2. **`triage_toolkit/evidence.py` is now a high-value dependency surface**
   - Shared evidence/ranking logic now feeds `summary`, `timeline`, and `runbook`.
   - `order_events(...)` carries the documented deterministic tie-break path, but there is still no dedicated `tests/test_evidence.py`.
   - Conclusion: focused evidence-helper tests are the strongest next payoff.

3. **`triage_toolkit/cli.py` concentrates cross-command behavior that still lacks focused helper tests**
   - Parse-summary aggregation, strict parse gates, bounded diagnostics carry-forward, and reusable filters all live here now.
   - Those rules affect multiple commands, but current protection is still mostly at the command/CLI layer.
   - Conclusion: helper-focused CLI tests should follow immediately after the evidence helper suite.

4. **`triage_toolkit/redaction.py` is tested end-to-end but not directly enough for regex-heavy changes**
   - Redaction touches parse diagnostics plus human-readable timeline/runbook outputs.
   - Existing CLI/timeline/runbook tests cover outcomes, but not the helper-level boundaries that are easiest to accidentally shift.
   - Conclusion: a direct redaction helper suite is the right third live item once evidence and CLI helper tests are queued first.

## Roadmap decisions derived from the current repo

### P1 — ITK-025: Add direct unit coverage for shared evidence and ranking helpers
**Why now:** evidence ordering and ranking behavior now spans several user-facing surfaces, so regressions should fail nearer to `evidence.py` instead of only through larger integration tests.

### P1 — ITK-026: Add direct unit coverage for shared CLI ingestion/filter/strict-gate helpers
**Why next:** shared CLI plumbing now carries core correctness rules for multiple commands, and the repo would benefit from faster fault localization there.

### P2 — ITK-027: Add direct unit coverage for shared redaction helpers and placeholder stability
**Why after that:** redaction already has good end-to-end coverage, but direct helper tests would lock regex ordering and false-positive boundaries before future changes land.

## Explicitly de-prioritized in this pass
- New parser-format expansion: nothing in the current repo evidence says new format support now outranks hardening shared helper behavior.
- Fresh output-shape feature work for `timeline` or `runbook`: those surfaces just received deterministic/evidence-oriented improvements and are not the highest-risk gap anymore.
- Reopening summary contract work as the top priority: that gap was closed by the existing `tests/test_summary_contract.py` suite.

## Risks / blockers to monitor
- ITK-025 must preserve the documented deterministic ordering contract, especially for tied timestamps with and without explicit source metadata.
- ITK-026 should test public behavior and invariants rather than pinning brittle incidental implementation details.
- ITK-027 needs to lock current redaction boundaries without making future placeholder additions unnecessarily painful.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-025 — direct evidence/ranking helper unit coverage
2. ITK-026 — direct CLI ingestion/filter/strict-gate helper coverage
3. ITK-027 — direct redaction helper and placeholder-stability coverage
