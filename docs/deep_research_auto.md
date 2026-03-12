Generated: 2026-03-12 18:09 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `README.md`
- `AGENTS.md`
- `docs/AI_EDIT_POLICY.md`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- live file-existence checks for the key docs requested in this pass
- live repo layout checks for `triage_toolkit/`, `tests/`, and `tests/fixtures/golden/`
- live repo status via `git status --short --branch`
- focused reads of `tests/test_main.py`, `tests/test_utils.py`, `tests/test_cli_helpers.py`, `triage_toolkit/cli.py`, and `triage_toolkit/utils.py`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` shows a docs-only working tree during this maintenance pass; no source-file changes were introduced for the refresh
- package footprint remains compact and reviewable:
  - 10 source modules under `triage_toolkit/`
  - 11 test modules under `tests/`
  - 138 top-level test functions
  - 15 golden fixtures under `tests/fixtures/golden/`
- dedicated helper suites already exist for:
  - shared CLI plumbing (`tests/test_cli_helpers.py`)
  - shared evidence/ranking logic (`tests/test_evidence.py`)
  - shared redaction behavior (`tests/test_redaction.py`)
- dedicated contract/golden coverage already exists for:
  - parse JSON (`tests/test_cli.py` + `tests/fixtures/golden/parse_output.json`)
  - redacted parse diagnostics (`tests/fixtures/golden/parse_output_redacted.json`)
  - summary JSON (`tests/test_summary_contract.py` + summary-specific goldens)
  - timeline markdown (`tests/test_timeline.py` + `tests/fixtures/golden/timeline_output.md`)
  - redacted timeline markdown (`tests/fixtures/golden/timeline_output_redacted.md`)
  - runbook markdown (`tests/test_runbook.py` + `tests/fixtures/golden/runbook_output.md`)
  - redacted runbook markdown (`tests/fixtures/golden/runbook_output_redacted.md`)
- dedicated cross-surface parity coverage exists:
  - `tests/test_output_parity.py` ✅ present
- latest recorded verification in `docs/status.md`: `make test` ✅ (`143 passed`)

## Architecture findings from repo evidence

### 1) The next highest-value gap remains direct CLI summary/redaction helper coverage
`docs/status.md` already records ITK-029 and ITK-030 as complete, so the old “parser helper hardening first” conclusion is stale. The public summary contract and redacted artifacts are covered end to end, but the helper seams that assemble the automation-facing summary payload and rewrite dropped-line diagnostics are still mostly protected indirectly.

Helpers still lacking focused direct coverage:
- `_top_items(...)`
- `_build_incident_summary(...)`
- `_redact_parse_summary(...)`

Why this remains first:
- `triage summary` is the machine-readable handoff surface most likely to feed downstream automation.
- parse redaction is the main share-safe diagnostics path.
- helper-level regressions here would be user-visible and harder to localize than broader contract failures.

Roadmap implication:
- **ITK-032 should stay first.**

### 2) User-visible CLI error/version paths now outrank lower-level utility cleanup
The strongest remaining user-facing weakness is in the operator surface around version reporting and bad-input failures.

Repo evidence:
- `tests/test_main.py` still contains only a single module-entrypoint smoke test.
- `triage_toolkit/cli.py` contains explicit failure branches for missing files, unreadable paths, directories, invalid UTF-8, and package-version fallback.
- those branches are important to actual CLI behavior, but they are still lightly or indirectly covered compared with the happy-path command suites.

Why this should move ahead of utility cleanup:
- it protects the only operator interface the product exposes
- it reduces regression risk in the paths users hit when things go wrong
- it complements existing happy-path and contract suites without duplicating them

Roadmap implication:
- **ITK-033 should be second, ahead of ITK-031.**

### 3) `utils.py` is still worth hardening, but it is now third
`utils.py` remains the smallest direct test surface in the ingestion stack:
- `tests/test_utils.py` is still intentionally tiny
- `extract_correlation_id(...)` has no direct coverage today
- timestamp helper edge coverage is still narrower than the parser stack depends on indirectly

Why it falls to third:
- the helper is important, but its direct user-visible surface is smaller than the summary/redaction helpers and the CLI failure/version paths above
- most breakage here would still tend to show up indirectly in parser/CLI suites

Roadmap implication:
- **ITK-031 remains open, but third.**

## Priority conclusions
1. **ITK-032 should remain first now**
   - It protects the automation-facing summary builder and redacted diagnostics helper seams.
   - It closes the highest-value remaining indirect-coverage gap.

2. **ITK-033 should move to second**
   - It hardens the only operator interface on version/error paths that matter in real use.
   - It has better engineering impact than lower-level helper cleanup because it covers user-visible failure behavior.

3. **ITK-031 should move to third**
   - It is still concrete and useful.
   - It is smaller-impact than the two CLI-centered hardening tasks above.

## Resulting active queue
1. ITK-032 — direct CLI summary/redaction helper coverage for ordering and placeholder invariants
2. ITK-033 — direct CLI operator-surface coverage for version fallback and input failure paths
3. ITK-031 — utility-edge coverage for timestamp normalization and correlation-ID extraction

## What changed vs the previous ordering
Previous committed queue:
1. ITK-029
2. ITK-032
3. ITK-031

Refreshed queue:
1. ITK-032
2. ITK-033
3. ITK-031

Meaning:
- ITK-029 is no longer open because `docs/status.md` records it as complete.
- ITK-033 is now explicitly tracked and placed ahead of ITK-031.
- ITK-031 stays open, but drops behind the more user-visible CLI operator-surface gap.

## Assumptions
- Prioritization is based on repo-local evidence and currently documented CLI/test surfaces, not on a freshly generated branch-coverage report.
- `docs/status.md` remains the authoritative record of the latest completed engineering milestone.
- No product redesign docs or external issue tracker inputs were part of this maintenance pass.

## Risks / blockers to watch
- **Summary-helper duplication**: ITK-032 should complement the contract/golden suites, not recreate them wholesale.
- **CLI failure overfitting**: ITK-033 should assert stable message fragments and exit behavior, not platform-specific errno text or Typer internals.
- **Utility-test sprawl**: ITK-031 should stay focused on helper edge cases rather than rebuilding parser end-to-end tests from below.
- **Docs drift risk**: this repo depends on `docs/status.md`, `docs/ai_todo.md`, and `docs/deep_research_auto.md` staying synchronized whenever the queue changes.

## Why this refresh was needed
The queue had already been partially updated in-flight, but the background research note was still one step behind the best ordering for the remaining open work. This pass brings the research note and live queue back into alignment and makes the next coding pass unambiguous:

**start with ITK-032, then ITK-033, then ITK-031.**
