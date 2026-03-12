Generated: 2026-03-12 16:30 UTC  
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

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` ✅ clean working tree in this maintenance pass
- package footprint remains compact and reviewable:
  - 10 source modules under `triage_toolkit/`
  - 11 test modules under `tests/`
  - 135 test functions total
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
- dedicated cross-surface parity coverage now exists:
  - `tests/test_output_parity.py` ✅ present
- latest recorded verification in `docs/status.md`: `make test` ✅ (`135 passed`)

## Architecture findings from repo evidence

### 1) The highest-value missing seam is now parser-helper hardening, not redacted artifact freezing
The previous research note was stale because it still treated redacted full-output goldens as the top missing regression net. That is no longer true: the repo now contains redacted golden fixtures for parse diagnostics, timeline markdown, and runbook markdown, and `docs/status.md` records ITK-030 as complete.

What remains relatively indirect:
- `_source_timestamp_provenance(...)`
- `_build_parse_summary(...)`
- `_build_dropped_line_diagnostic(...)`
- explicit `source_order` propagation through `parse_lines_with_summary(...)`

Roadmap implication:
- **ITK-029 should now be first** because parser helpers still sit at the ingestion root used by every command.

### 2) The next best leverage is direct helper coverage for summary construction and parse-diagnostic redaction
The repo already has strong end-to-end coverage for the public summary JSON contract and redacted outputs. What is still mostly indirect is the CLI helper layer that assembles the ranked summary payload and rewrites dropped-line diagnostics during `--redact`.

Helpers still lacking focused direct coverage:
- `_top_items(...)`
- `_build_incident_summary(...)`
- `_redact_parse_summary(...)`

Why this matters:
- `triage summary` is the machine-readable handoff surface for automation.
- parse redaction is the main share-safe diagnostics path.
- helper-level regressions here could stay annoyingly hard to localize even if broader contract tests eventually catch them.

Roadmap implication:
- **Add a new second-priority task for direct CLI summary/redaction helper coverage**.

### 3) `utils.py` remains the smallest direct test surface in the ingestion stack
`utils.py` is still tiny, but it owns behaviors that cascade through every parse path:
- timestamp normalization / acceptance boundaries
- correlation-ID extraction from unstructured text

Current posture:
- timestamp normalization has some focused direct coverage
- `extract_correlation_id(...)` is still exercised mostly indirectly through parser/evidence paths

Roadmap implication:
- keep this as the third task after parser hardening and CLI summary-helper hardening
- it is still useful, but it is now clearly cleanup/hardening rather than first-line risk reduction

## Priority conclusions
1. **ITK-029 should be first now**
   - It strengthens the ingestion root that feeds every command.
   - It closes the most important remaining indirect helper gap after ITK-030 landed.

2. **ITK-032 should be second**
   - It adds direct coverage for the helper layer behind the automation-facing summary contract and redacted parse diagnostics.
   - It is a better next investment than generic utility cleanup because it protects more user-visible behavior.

3. **ITK-031 should be third**
   - It is still worthwhile and concrete.
   - It remains smaller-impact than the two higher-leverage helper hardening tasks above.

## Resulting active queue
1. ITK-029 — parser helper coverage for provenance, diagnostics builders, and source-order propagation
2. ITK-032 — direct CLI summary/redaction helper coverage for ordering and placeholder invariants
3. ITK-031 — utility-edge coverage for timestamp normalization and correlation-ID extraction

## Assumptions
- Prioritization is based on repo-local evidence and the currently documented CLI/test surfaces, not on a freshly generated branch-coverage report.
- `docs/status.md` remains the authoritative record of the latest completed engineering milestone.
- No product redesign docs or external issue tracker inputs were part of this maintenance pass.

## Risks / blockers to watch
- **Parser-helper overfitting**: ITK-029 should lock documented invariants and public semantics, not private loop trivia.
- **Summary-helper duplication**: ITK-032 should complement the contract/golden suites, not recreate them wholesale.
- **Utility-test sprawl**: ITK-031 should stay focused on helper edge cases rather than rebuilding parser end-to-end tests from below.
- **Docs drift risk**: this repo depends on `docs/status.md`, `docs/ai_todo.md`, and `docs/deep_research_auto.md` staying synchronized whenever the queue changes.

## Why this refresh was needed
The previous note was one pass behind the live repo. It still described:
- ITK-030 as the top missing task even though it is now complete
- pre-refresh conclusions about redacted fixtures being absent
- a shorter open queue than the requested 3-7 actionable items

This refresh brings the research note back in line with the actual repo state and makes the next coding pass unambiguous: start with ITK-029.
