Generated: 2026-03-12 13:49 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `README.md`
- `pyproject.toml`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `triage_toolkit/cli.py`
- `triage_toolkit/parser.py`
- `triage_toolkit/evidence.py`
- `triage_toolkit/timeline.py`
- `triage_toolkit/runbook.py`
- `triage_toolkit/models.py`
- `triage_toolkit/utils.py`
- `tests/test_cli.py`
- `tests/test_parser.py`
- `tests/test_summary_contract.py`
- `tests/test_timeline.py`
- `tests/test_runbook.py`
- `tests/test_utils.py`
- live file-existence checks for the key docs/test surfaces referenced by the queue
- repo status via `git status --short --branch`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` ⚠️ `main...origin/main` with pre-existing docs-only modifications already present in:
  - `docs/status.md`
  - `docs/user_todo.md`
- package footprint remains compact and legible:
  - 10 source modules under `triage_toolkit/`
  - 10 test modules under `tests/`
  - 130 test functions total
  - 11 golden fixtures under `tests/fixtures/golden/`
- dedicated helper suites already exist for:
  - shared CLI plumbing (`tests/test_cli_helpers.py`)
  - shared evidence/ranking logic (`tests/test_evidence.py`)
  - shared redaction behavior (`tests/test_redaction.py`)
- dedicated non-redacted contract/golden coverage already exists for:
  - parse JSON (`tests/test_cli.py` + `tests/fixtures/golden/parse_output.json`)
  - summary JSON (`tests/test_summary_contract.py` + summary-specific goldens)
  - timeline markdown (`tests/test_timeline.py` + `tests/fixtures/golden/timeline_output.md`)
  - runbook markdown (`tests/test_runbook.py` + `tests/fixtures/golden/runbook_output.md`)
- `tests/test_output_parity.py` ❌ still missing
- redacted golden fixtures ❌ still missing
- latest recorded verification in `docs/status.md`: `make test` ✅ (`130 passed`)

## Architecture findings from repo evidence

### 1) The architecture is intentionally layered around one ingestion path plus shared evidence semantics
The repo is small, but the layering is clean and now stable enough that regression risk comes more from **cross-surface drift** than from missing basic functionality.

Observed structure:
- `utils.py` → timestamp normalization and correlation-ID extraction
- `parser.py` → heterogeneous line parsing + parse summary/diagnostics + provenance assignment
- `cli.py` → strict gates, multi-input/stdin orchestration, filtering, output writing, schema versioning
- `evidence.py` → ordering, error classification, signature/source/component ranking, representative IDs
- `redaction.py` → deterministic placeholder generation for sensitive values
- `timeline.py` / `runbook.py` → markdown renderers over shared ordered/evidence slices

Implication:
- The core product risk is no longer “can it parse logs at all?”
- The bigger risk is “do all user-facing surfaces still tell the same story about the same incident slice?”

### 2) Contract coverage is broad for individual surfaces, but not yet for cross-surface agreement
The repo already locks a lot of behavior:
- parse contract/golden output exists
- summary contract/golden outputs exist for single-input, multi-input, file+stdin, and filter-miss cases
- timeline and runbook each have golden coverage plus focused deterministic/evidence tests
- helper-level unit tests exist for CLI plumbing, evidence ranking, and redaction internals

What is still not locked:
- there is no single parity suite that feeds one fixture into `summary`, `timeline`, and `runbook` and proves they agree on:
  - incident window boundaries
  - evidence-event counts
  - signature ordering
  - evidence-by-source ordering
  - empty-slice behavior

Roadmap implication:
- **ITK-028 remains the highest-leverage task** because it guards the shared architecture at the seam where three operator-facing outputs meet.

### 3) Redaction is implemented as a real product feature, but its full outputs are not yet frozen
Repo evidence shows redaction is no longer a toy helper:
- `cli.py` exposes `--redact` on parse/timeline/runbook
- `redaction.py` is shared across diagnostics and markdown surfaces
- direct helper tests plus substring-level CLI/timeline/runbook tests already exist

But the full operator-visible artifacts are not frozen with goldens yet.
That means regressions like these could sneak through even with current tests passing:
- placeholder placement changing inside markdown lists/tables
- section order drifting in redacted timeline/runbook outputs
- JSON diagnostic structure staying valid while the redacted text loses consistency/readability

Roadmap implication:
- move redacted full-output goldens ahead of lower-level parser hardening because this protects a public, safety-relevant surface that users are likely to share.

### 4) Parser behavior is already tested well at the public level, so remaining parser work is now mostly hardening
`tests/test_parser.py` already covers a fair amount:
- JSON vs text parsing happy paths
- timestamp normalization and provenance on successful events
- dropped-line summaries and bounded diagnostics
- stable stdin/source labeling
- event contract keys
- streaming behavior and large-input summary behavior

What remains mostly indirect:
- `_source_timestamp_provenance(...)`
- `_build_parse_summary(...)`
- `_build_dropped_line_diagnostic(...)`
- explicit `source_order` propagation assertions at the parser-helper layer

Roadmap implication:
- parser hardening still matters because every command depends on it, but it now sits behind parity and redacted full-output protection in raw leverage.

### 5) Utility coverage is the smallest direct test surface left under the ingestion stack
`utils.py` is tiny, but it is still the root for:
- UTC normalization behavior
- timestamp acceptance/rejection boundaries
- correlation-ID extraction used by parser/evidence consumers

Current direct coverage is intentionally light:
- `parse_timestamp(...)` has a small focused suite
- `extract_correlation_id(...)` behavior is exercised mostly indirectly via parser tests rather than directly in `tests/test_utils.py`

Roadmap implication:
- this is a reasonable low-priority hardening task after the higher-signal shared-surface tests land.

## Priority conclusions
1. **ITK-028 should stay first**
   - It addresses the highest-risk architectural seam: shared incident semantics across three user-facing outputs.
   - The missing file is obvious (`tests/test_output_parity.py`), and the acceptance criteria are concrete.

2. **ITK-030 should move ahead of ITK-029**
   - Parser public behavior is already broadly covered.
   - Redacted outputs are public/safety-facing and still lack full-output goldens.
   - This gives better leverage on real operator artifacts before doing more internal hardening.

3. **ITK-029 remains important, but now as hardening rather than the next most urgent gap**
   - It should lock helper/builder invariants without overfitting to private implementation trivia.

4. **ITK-031 is worth adding as the next low-noise backlog item**
   - `utils.py` is small enough that a narrow direct suite would be cheap and useful.
   - It keeps the live queue concrete without padding it with vague refactor work.

## Resulting active queue
1. ITK-028 — fixture-driven cross-surface parity for `summary` / `timeline` / `runbook`
2. ITK-030 — full redacted golden fixtures for parse diagnostics, timeline, and runbook
3. ITK-029 — parser helper coverage for provenance / diagnostics / source-order invariants
4. ITK-031 — direct utility-edge coverage for timestamp normalization and correlation-ID extraction

## Assumptions
- Prioritization is based on static repo evidence plus the existing docs/test layout, not on fresh runtime coverage metrics from a new test run.
- The working-tree doc modifications visible in `git status` are intentional/pre-existing and not evidence of product breakage.
- The current product intent remains the README-described CLI contract rather than a pending redesign.

## Unknowns
- No fresh `coverage.py` report was generated in this maintenance pass, so gap ranking is inferred from test/module structure rather than branch-level coverage numbers.
- No external issue tracker / production incident history was consulted, so prioritization is based on architectural leverage, not live customer pain.
- No external web validation was needed for this pass; the repo itself provided enough signal for prioritization.

## Risks / blockers to watch
- **Working tree is not clean**: future coding passes should avoid assuming a pristine baseline because docs are already modified.
- **ITK-028 risk**: the parity suite must compare semantics, not brittle presentation details from markdown formatting.
- **ITK-030 risk**: redacted goldens can become fixture-maintenance drag if the sensitive fixture is too large; keep it compact and deterministic.
- **ITK-029 risk**: helper hardening should lock documented invariants, not private iteration quirks.
- **ITK-031 risk**: utility tests should complement parser tests, not duplicate them.

## Why this refresh was needed
The previous deep-research note was still anchored to the prior maintenance pass. The live repo evidence now shows:
- the working tree is docs-dirty rather than clean
- the shared helper suites are in place
- the highest remaining architecture-level gap is still cross-surface parity
- the next-best public-surface protection is redacted full-output freezing, which now outranks additional parser-helper hardening

This refresh brings the background note back in sync with the live repo and gives `docs/ai_todo.md` a tighter, more evidence-backed queue.
