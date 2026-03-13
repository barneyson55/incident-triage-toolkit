Generated: 2026-03-13 UTC  
Repository: `incident-triage-toolkit`  
Repo root reviewed: `/home/node/.openclaw/workspace/projects/auto-senior-pm/repos/incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `README.md`
- `pyproject.toml`
- `docs/AI_EDIT_POLICY.md`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- `triage_toolkit/cli.py`
- `triage_toolkit/parser.py`
- `triage_toolkit/timeline.py`
- `triage_toolkit/runbook.py`
- `tests/test_cli.py`
- `tests/test_cli_helpers.py`
- `tests/test_main.py`
- `tests/test_timeline.py`
- `tests/test_runbook.py`
- live file-existence checks for the key docs requested in this pass
- live repo status via `git status --short --branch`
- live verification via `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q`
- one minimal external standards check on GitHub Flavored Markdown table behavior (`github.github.com/gfm/` plus search results pointing to escaped pipes / single-line table-cell expectations)

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

Missing `status` / `critical_todo` files would have been acceptable per the maintenance brief, but both are present in this repo.

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry (`## main...origin/main`)
- `docs/user_todo.md` exists and has no open checkbox items
- live coverage check:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`186 passed`)
  - total coverage: `99%`
  - uncovered lines are now limited to:
    - `triage_toolkit/cli.py:102,148,264,397,522`
    - `triage_toolkit/parser.py:265-266`
- live file structure confirms a deliberately small package:
  - source modules: `cli`, `parser`, `utils`, `models`, `evidence`, `redaction`, `timeline`, `runbook`, plus package entrypoints
  - test modules: 11 top-level files with golden fixtures and parity coverage already in place
  - runtime dependency surface: one direct runtime dependency in `pyproject.toml` (`typer==0.21.1`)

## Architecture map from repo evidence
### 1) Ingestion and normalization are already well-factored
- `parser.py` owns line parsing, alias-key normalization, provenance capture, and dropped-line diagnostics.
- `utils.py` owns timestamp normalization and correlation-ID extraction.
- `models.py` carries the normalized event model plus source-order tie-break metadata.

Interpretation:
- Core ingestion semantics are centralized and already mature.
- The repo is no longer in a “missing fundamentals” state; most remaining work is contract hardening and operator-surface polish.

### 2) `cli.py` is the integration hub and contract seam
- `cli.py` owns:
  - file/stdin ingestion orchestration
  - aggregate parse summaries
  - strict parse gates
  - shared filter semantics
  - write-path behavior
  - Typer command wiring and entrypoints

Interpretation:
- The remaining `cli.py` uncovered lines are meaningful mostly because they sit on user-visible seams, not because they hide complex logic.
- After the current maturity level, one uncovered line in `cli.py` can matter more than several uncovered parser internals.

### 3) Shared incident semantics are centralized correctly
- `evidence.py` drives shared error/evidence ranking used by `summary`, `timeline`, and `runbook`.
- `redaction.py` provides shared deterministic placeholder logic.
- Existing test files (`test_evidence.py`, `test_redaction.py`, `test_output_parity.py`, `test_summary_contract.py`) already lock most cross-surface invariants.

Interpretation:
- The repo is architecturally set up for low-risk hardening.
- New work should continue targeting small seam-specific regressions rather than broad refactors.

### 4) Markdown rendering is now the most obvious product-risk seam
Repo evidence:
- `timeline.py` escapes markdown pipes only for `source` and `message` via `_escape_markdown(...)`.
- `timeline.py` does **not** escape `event.component` before inserting it into the markdown table row.
- `runbook.py` and `timeline.py` flatten message newlines in some paths (`event.message.replace("\n", " ")`), but there is no focused contract coverage proving all operator-facing dynamic strings remain single-line and markdown-safe.
- `parser.py` accepts arbitrary string values for JSON aliases such as component/service/logger fields, so unusual strings can reach the renderers.

Interpretation:
- At current repo maturity, the biggest remaining engineering risk is probably not “can we parse the log?” but “can we trust the generated handoff artifact under ugly-but-valid input?”
- This makes markdown-safety hardening a better next priority than generic pursuit of 100% coverage.

## Minimal external validation
External check was intentionally tiny and only used to validate the markdown-rendering concern:
- GitHub Flavored Markdown spec (`https://github.github.com/gfm/`) confirms tables are an extension and notes block-level elements cannot be inserted into a table.
- Search results from GitHub Docs / GFM-oriented references consistently describe literal pipes as requiring escaping and multi-line table content as problematic unless flattened or otherwise constrained.

Use of external evidence here is limited to supporting the repo-derived conclusion that `|` and embedded newlines are worth treating as renderer-safety inputs.

## Evidence-based roadmap conclusions
### Highest-impact next step: operator-facing markdown safety
Why this moved up:
- The suite is already green and at 99% coverage.
- Parse alias handling, redaction, parity, and summary contracts are already directly covered.
- Timeline/runbook outputs are the human handoff surfaces most likely to cause visible confusion under edge input.

Recommended task shape:
- add narrow tests for pipe/newline corruption in timeline and runbook
- fix only the minimal renderer helpers exposed by those tests
- avoid golden churn unless a whole-surface contract truly changes

### Second step: README quickstart/write-path parity for `summary`
Why this deserves its own item:
- README quickstart shows file-output flows for all commands.
- Parse/timeline/runbook already have file-output success tests.
- `summary` is the remaining user-visible gap and maps directly to one uncovered `cli.py` line.

Recommended task shape:
- one CLI-level test
- assert both success messaging and written JSON contract
- no broader refactor

### Third step: mop up the truly thin glue branches
Remaining blind spots after the two items above:
- `_read_stdin_lines()` fallback without `.buffer`
- `_read_events_for_parse([])`
- no-filter passthrough in `_apply_event_filters(...)`
- `parse_file(...)`
- `triage_toolkit.cli` script/module entrypoint line

Interpretation:
- these are worthwhile, but they are cleanup, not roadmap-driving work

## What changed vs the previous research note
The prior research note was stale in two ways:
1. It still treated alias-heavy CLI contract work as the top open item even though `docs/status.md` and current tests show that work is already completed.
2. It treated markdown formatting mostly as a generic coverage hole, while the live code review shows a more specific architectural risk: timeline escapes only some dynamic table fields, not all of them.

The refreshed priority order is therefore:
1. `ITK-034` — markdown-safety hardening for timeline/runbook
2. `ITK-038` — `summary --out <file>` quickstart/write-path parity
3. `ITK-036` — thin helper/wrapper cleanup

## Assumptions
- Primary markdown consumers are GFM-like renderers (GitHub, similar markdown viewers, or tooling with comparable table behavior).
- Operator-facing timeline/runbook artifacts matter more than squeezing out a nominal last percent of coverage.
- The current product intent remains the one documented in `README.md`: compact Python CLI, boring dependency surface, deterministic outputs.

## Unknowns
- No production telemetry or issue tracker was reviewed here, so real-world frequency of malformed `component` strings or newline-heavy fields is unknown.
- No user interviews or support transcripts were reviewed, so operator pain is inferred from repo architecture and contract surfaces rather than direct feedback.
- It remains unknown whether future roadmap should include broader ingest features (for example multiline stack traces or configurable field maps); this pass intentionally stayed grounded in currently documented behavior and live coverage gaps.

## Risks / blockers
- No blocker escalation is needed right now: `docs/critical_todo.md` exists and is empty (`- (none)`).
- Main risk is priority drift back toward low-value coverage vanity work; the repo is mature enough that user-visible contract safety should stay ahead of tiny helper gaps.
- Keep new tests narrow. This repo benefits from compact, seam-specific assertions more than broad golden rewrites.
