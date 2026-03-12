Generated: 2026-03-12 UTC  
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
- live repo status via `git status --short --branch`
- live repo layout checks for `triage_toolkit/`, `tests/`, and `tests/fixtures/`
- focused reads of `triage_toolkit/parser.py`, `triage_toolkit/utils.py`, `triage_toolkit/timeline.py`, `triage_toolkit/runbook.py`, `tests/test_parser.py`, `tests/test_utils.py`, `tests/test_timeline.py`, `tests/test_runbook.py`, `tests/test_cli_helpers.py`, `tests/test_main.py`, and `tests/test_output_parity.py`
- focused symbol/test searches across the repo for remaining direct-coverage gaps

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry to this maintenance pass (`## main...origin/main`)
- package footprint remains compact and reviewable:
  - 10 source modules under `triage_toolkit/`
  - 11 top-level test modules under `tests/`
  - 148 top-level test functions
  - 18 tracked fixture files under `tests/fixtures/`
- dedicated helper suites already exist for:
  - shared CLI plumbing (`tests/test_cli_helpers.py`)
  - shared evidence/ranking logic (`tests/test_evidence.py`)
  - shared redaction behavior (`tests/test_redaction.py`)
- dedicated contract/golden coverage already exists for:
  - parse JSON
  - redacted parse diagnostics
  - summary JSON
  - timeline markdown
  - redacted timeline markdown
  - runbook markdown
  - redacted runbook markdown
  - cross-surface parity (`tests/test_output_parity.py`)
- latest recorded verification in `docs/status.md`: `make test` ✅ (`153 passed`)

## Architecture findings from repo evidence

### 1) `utils.py` is now the top open hardening target
This is the smallest direct test surface still sitting underneath every ingest path.

Live repo evidence shows:
- `tests/test_utils.py` still contains only five direct tests
- `extract_correlation_id(...)` still has no direct coverage
- timestamp normalization still lacks direct cases for microseconds, `Z` parsing breadth, space-vs-`T` separators, and malformed offset shapes

Why it should lead now:
- ITK-033 is already completed and moved out of the active queue
- `utils.py` is called on both text and JSON parse paths, so regressions propagate widely
- the work is narrow, coverage-first, and easy to verify without changing public contracts

Roadmap implication:
- **ITK-031 should be first.**

### 2) Parser alias branches are important and still under-locked
The parser claims heterogeneous log support, and the code explicitly accepts multiple JSON key aliases. The suite still leans heavily on the default key names.

Live repo evidence shows:
- `parser.py` supports `timestamp|time|ts`
- `parser.py` supports `level|severity|lvl`
- `parser.py` supports `component|service|logger`
- `parser.py` supports `message|msg|event`
- correlation IDs can come from payload `correlation_id`, payload `cid`, or message extraction
- current parser tests do not directly lock most of those alias/precedence branches

Why this belongs near the top:
- this is core ingestion behavior, not cosmetic output behavior
- regressions here would silently drop or flatten supported vendor log shapes
- the required tests are concrete and parser-local

Roadmap implication:
- **add ITK-035 as the second active item.**

### 3) Human-facing renderer edge cases remain the next best user-visible gap
The timeline and runbook outputs are well covered for happy paths, determinism, redaction, provenance, and empty states. They still lack focused assertions for formatting edge cases that can quietly degrade handoff quality.

Live repo evidence shows:
- `timeline.py` explicitly escapes `|` characters in table cells
- `timeline.py` and `runbook.py` explicitly flatten embedded newlines before rendering messages/examples
- current tests assert many content and ordering behaviors, but not those formatting-specific guardrails

Why this should stay active:
- malformed markdown is still an operator-facing regression
- the work is narrow and verifiable
- it should come after the parser-facing gaps above, not before them

Roadmap implication:
- **ITK-034 should be third.**

## Priority conclusions
1. **ITK-031 should be first now**
   - direct utility coverage is still much smaller than the parser stack depends on
   - especially `extract_correlation_id(...)` and timestamp-shape edges

2. **ITK-035 should be second**
   - parser alias/precedence support is part of the core heterogeneous-ingestion promise
   - the current suite does not directly lock most of those branches

3. **ITK-034 should be third**
   - it protects human-facing markdown quality on pipe/newline/provenance formatting edges that are implemented but not directly frozen

## Resulting active queue
1. ITK-031 — add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
2. ITK-035 — lock heterogeneous JSON-ingestion aliases and correlation-ID precedence with direct parser coverage
3. ITK-034 — add focused markdown-renderer edge coverage for timeline/runbook safety and readability

## What changed vs the previous ordering
Previous open queue in practice:
1. ITK-033
2. ITK-031
3. ITK-034

Refreshed queue:
1. ITK-031
2. ITK-035
3. ITK-034

Meaning:
- completed ITK-033 is removed from the active queue and kept only in the completed section of `docs/ai_todo.md`
- ITK-031 becomes the clear first unchecked item
- ITK-035 is added to capture a real parser-support gap that was not previously called out explicitly
- ITK-034 remains active, but behind the parser-facing items

## Risks / blockers to watch
- **Status-doc drift:** `docs/status.md` still says `Next` is ITK-031 but does not mention the new ITK-035 follow-on; this refresh intentionally updated the planning docs only.
- **Parser-test sprawl:** ITK-035 should lock alias and precedence branches directly instead of turning into another broad end-to-end parser rewrite.
- **Utility-test sprawl:** ITK-031 should stay focused on helper edges instead of recreating parser coverage from below.
- **Renderer-test sprawl:** ITK-034 should use narrow rendered-fragment assertions, not broad golden churn.

## Why this refresh was needed
The previous queue had gone stale in two ways:
1. it still treated completed ITK-033 as an active priority
2. it did not call out the parser's untested JSON alias/precedence branches, which are more central to the product promise than another round of renderer-only hardening

This refresh makes the next coding pass unambiguous:
- **start with ITK-031**
- then **ITK-035**
- then **ITK-034**
