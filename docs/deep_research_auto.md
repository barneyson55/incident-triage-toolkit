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
- focused reads of `tests/test_main.py`, `tests/test_utils.py`, `triage_toolkit/cli.py`, `triage_toolkit/utils.py`, `triage_toolkit/timeline.py`, and `triage_toolkit/runbook.py`
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
  - 142 top-level test functions
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
- latest recorded verification in `docs/status.md`: `make test` ✅ (`147 passed`)

## Architecture findings from repo evidence

### 1) The highest-value remaining gap is narrower than the previous queue said
The pre-refresh queue treated version fallback and basic file-read failures as broadly undercovered. That is no longer accurate.

Live repo evidence shows:
- `tests/test_cli.py` already directly covers `_get_version()` fallback
- `tests/test_cli.py` already directly covers the `--version` flag
- `tests/test_cli.py` already directly covers `_read_events(...)` error mapping

What is still thin:
- direct helper coverage for `_read_events_with_summary(...)`
- direct helper coverage for `_read_events_from_stdin(...)`
- a stronger `tests/test_main.py` surface beyond one module-entrypoint smoke test

Why this now belongs first:
- these are still operator-facing code paths inside the only user interface the tool exposes
- they are more user-visible than the lower-level helper/test gaps below
- the task can now be scoped more tightly and verified more cleanly than the stale wording suggested

Roadmap implication:
- **ITK-033 should lead the open queue, but with a narrower, more accurate definition.**

### 2) `utils.py` remains the next best hardening target
`tests/test_utils.py` still contains only five direct tests.

Live repo evidence:
- `parse_timestamp(...)` has direct coverage only for a small set of obvious cases
- `extract_correlation_id(...)` still has no direct tests
- the parser stack depends on these helpers on every ingest path, even though larger parser/CLI suites would catch only some regressions indirectly

Why this stays second:
- it underpins every parse path
- it is still materially undercovered compared with the rest of the repository
- it remains simpler and lower-risk than broader renderer or contract work

Roadmap implication:
- **ITK-031 should stay open and move to second.**

### 3) Human-facing renderer edge cases deserve a focused third item
The timeline and runbook outputs are well covered for happy paths, determinism, redaction, provenance, and empty states. But there is still no focused coverage for formatting edge cases that can quietly degrade operator handoff quality.

Live repo evidence:
- `timeline.py` explicitly escapes `|` characters in table cells
- `timeline.py` and `runbook.py` explicitly flatten embedded newlines before rendering messages/examples
- current tests assert many content and ordering behaviors, but not those formatting-specific guardrails

Why this is worth tracking separately:
- malformed markdown is a real operator-facing regression even if parsing still works
- the required tests are narrow and concrete
- it adds confidence without changing any product contract

Roadmap implication:
- **add ITK-034 as the third active item.**

## Priority conclusions
1. **ITK-033 should be first now**
   - not because version coverage is missing wholesale, but because the remaining direct CLI-helper/operator-surface seams are still thinner than the rest of the repo
   - especially `_read_events_with_summary(...)`, `_read_events_from_stdin(...)`, and the thin `tests/test_main.py` surface

2. **ITK-031 should be second**
   - direct utility coverage is still much smaller than the parser stack depends on
   - especially for `extract_correlation_id(...)` and timestamp-shape edges

3. **ITK-034 should be third**
   - it protects human-facing markdown quality on pipe/newline/provenance formatting edges that are implemented but not directly locked

## Resulting active queue
1. ITK-033 — close remaining direct CLI operator-surface coverage gaps for file-summary/stdin failure paths and entrypoint behavior
2. ITK-031 — add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
3. ITK-034 — add focused markdown-renderer edge coverage for timeline/runbook safety and readability

## What changed vs the previous ordering
Previous open queue in practice:
1. ITK-033 (with stale wording that overstated missing version coverage)
2. ITK-031

Refreshed queue:
1. ITK-033 (narrowed to the real remaining helper/entrypoint gaps)
2. ITK-031
3. ITK-034

Meaning:
- completed ITK-032 is removed from the active queue and kept only in the completed section
- ITK-033 stays first, but is rewritten to match the actual live repo evidence instead of stale assumptions
- ITK-031 remains open and second
- ITK-034 is added so the active queue stays within the requested 3-7 concrete items and captures the highest remaining user-visible formatting gap

## Risks / blockers to watch
- **Docs drift:** `docs/status.md` still says `Next` is ITK-033 and records older verification numbers; this refresh intentionally updates only `docs/ai_todo.md` / `docs/deep_research_auto.md`, so status-note drift remains a documentation risk until a normal coding milestone updates `docs/status.md` again.
- **CLI failure overfitting:** ITK-033 should assert stable message fragments and helper call behavior, not platform-specific errno wording or Typer implementation details.
- **Utility-test sprawl:** ITK-031 should stay focused on helper edges instead of recreating parser end-to-end coverage.
- **Renderer-test sprawl:** ITK-034 should lock markdown safety/readability edges with small focused assertions, not trigger broad golden churn.

## Why this refresh was needed
The previous queue had two problems:
1. it still carried a completed milestone (`ITK-032`) in the active section
2. it described some CLI version/error gaps more broadly than the live repo evidence supports now

This refresh makes the next coding pass unambiguous:
- **start with ITK-033**
- then **ITK-031**
- then **ITK-034**
