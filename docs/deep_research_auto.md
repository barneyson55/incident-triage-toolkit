Generated: 2026-03-12 15:07 UTC  
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
- live file-existence checks for the key docs/test surfaces referenced by the queue
- repo status via `git status --short --branch`
- test/layout verification for the current regression surfaces under `tests/`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` ✅ `main...origin/main` (working tree clean)
- package footprint remains compact and legible:
  - 10 source modules under `triage_toolkit/`
  - 11 test modules under `tests/`
  - 133 test functions total
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
- dedicated cross-surface parity coverage now exists:
  - `tests/test_output_parity.py` ✅ present with 3 filtered-slice parity tests
- redacted golden fixtures are still missing:
  - no `tests/fixtures/golden/*redact*` files yet
- latest recorded verification in `docs/status.md`: `make test` ✅ (`133 passed`)

## Architecture findings from repo evidence

### 1) The repo’s biggest remaining gap has moved from cross-surface parity to redacted full-output freezing
The previous maintenance pass was still justified in putting parity first. That changed once ITK-028 landed and `tests/test_output_parity.py` started locking the shared filtered-slice seam across `summary`, `timeline`, and `runbook`.

What that means now:
- the highest-risk *missing* regression net is no longer semantic parity across surfaces
- it is the lack of end-to-end goldens for the redacted operator-facing artifacts those surfaces emit

### 2) Redaction is a public/safety-facing feature, but its full artifacts are still only partially locked
Repo evidence now shows three layers of redaction protection:
- helper-level unit coverage in `tests/test_redaction.py`
- targeted CLI assertions in `tests/test_cli.py`
- targeted renderer assertions in `tests/test_timeline.py` and `tests/test_runbook.py`

What is still not frozen:
- the full redacted parse diagnostics JSON artifact
- the full redacted timeline markdown artifact
- the full redacted runbook markdown artifact

That leaves room for regressions such as:
- placeholder placement drift inside markdown bullets/tables
- section-order drift in redacted outputs while targeted assertions still pass
- artifact-level formatting drift that keeps substrings intact but changes the actual handoff document shape

Roadmap implication:
- **ITK-030 is now the highest-leverage remaining task**.

### 3) Parser work is still important, but now it is clearly hardening rather than first-line risk reduction
`tests/test_parser.py` already covers the public parser behaviors that matter most:
- JSON vs text parsing
- deterministic dropped-line summaries/diagnostics
- stdin/source labeling
- provenance on successful events
- streaming behavior and large-input summaries
- current event contract keys

What remains mostly indirect:
- `_source_timestamp_provenance(...)`
- `_build_parse_summary(...)`
- `_build_dropped_line_diagnostic(...)`
- explicit `source_order` propagation through parser helpers

Roadmap implication:
- parser helper hardening stays worthwhile, but it now sits behind the public/safety-facing redacted goldens.

### 4) `utils.py` is still the smallest direct test surface in the ingestion stack
`utils.py` remains tiny, but it still owns two behaviors that cascade through the whole CLI:
- timestamp normalization / acceptance boundaries
- correlation-ID extraction from unstructured text

Current direct test posture is still narrow:
- timestamp normalization has a small focused suite
- `extract_correlation_id(...)` is still validated mostly indirectly via parser/evidence behavior

Roadmap implication:
- this remains a good low-noise backlog item after the more leveraged redaction and parser tasks.

## Priority conclusions
1. **ITK-030 should be first now**
   - It protects a user-facing safety feature that is currently missing full-output contract freezing.
   - It has concrete deliverables and clear focused verification commands.

2. **ITK-029 should remain second**
   - Parser helper coverage still strengthens the ingestion root used by every command.
   - The work is meaningful, but less leveraged than end-to-end redacted artifact protection.

3. **ITK-031 should remain third**
   - Utility-edge tests are cheap and useful, but they are now clearly cleanup/hardening compared with the higher-priority gaps above.

## Resulting active queue
1. ITK-030 — full redacted golden fixtures for parse diagnostics, timeline, and runbook
2. ITK-029 — parser helper coverage for provenance / diagnostics / source-order invariants
3. ITK-031 — direct utility-edge coverage for timestamp normalization and correlation-ID extraction

## Assumptions
- Prioritization is based on repo-local evidence and the currently documented CLI/test surfaces, not on a freshly generated coverage report.
- The README-described product contract is still the intended public surface; no pending redesign docs were found in this pass.
- `docs/status.md` remains the authoritative record of the latest completed engineering milestone.

## Unknowns
- No fresh branch-coverage report was generated in this maintenance pass, so the ranking is based on architecture/test-surface leverage rather than uncovered-line counts.
- No external issue tracker, telemetry, or production incident history was consulted.
- No new runtime tests were executed in this pass because the task was docs-only reprioritization, not implementation.

## Risks / blockers to watch
- **Redacted golden maintenance drag**: ITK-030 should use one small sensitive fixture so the goldens stay reviewable instead of turning into noisy blobs.
- **Parser helper overfitting**: ITK-029 should lock documented invariants and public semantics, not incidental loop order or private implementation trivia.
- **Utility-test duplication**: ITK-031 should complement parser tests, not recreate end-to-end coverage at the helper layer.
- **Docs drift risk**: this repo relies on `docs/status.md`, `docs/ai_todo.md`, and `docs/deep_research_auto.md` staying in sync; future maintenance passes should refresh all three together when priorities shift.

## Why this refresh was needed
The previous deep-research note was one pass behind the live repo. Specifically, it still assumed:
- a docs-dirty working tree
- pre-ITK-028 test/module counts
- parity as the next missing seam instead of a completed regression surface

This refresh brings the research note back in line with the current repo state and makes the next coding pass unambiguous: start with ITK-030.
