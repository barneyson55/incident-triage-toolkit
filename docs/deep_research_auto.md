# deep_research_auto.md

Generated: 2026-02-17 12:13 UTC  
Repository: `incident-triage-toolkit`  
Scope: architecture/roadmap deep-research pass to keep `docs/ai_todo.md` continuously actionable and impact-prioritized.

## Method

### Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `README.md`
- `triage_toolkit/{cli.py,parser.py,utils.py,timeline.py,runbook.py,models.py,__main__.py}`
- `tests/{test_cli.py,test_parser.py,test_timeline.py,test_runbook.py,test_main.py}`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `Makefile`

### Local verification run
- `make lint` ✅
- `make test` ✅ (22 passed)
- `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=85` ✅ (85.46%)

### Minimal external validation used
- JSON Lines framing requirements (UTF-8, one JSON value per line): https://jsonlines.org/
- RFC 3339 UTC + offset timestamp profile: https://www.rfc-editor.org/rfc/rfc3339
- `pytest-cov` coverage gate option (`--cov-fail-under`): https://pytest-cov.readthedocs.io/en/stable/config.html
- Typer testing pattern via `CliRunner`: https://typer.tiangolo.com/tutorial/testing/

---

## Architecture snapshot (repo-grounded)

1. **Strict parse-quality gates are now consistently wired across all user-facing commands**
   - `parse`, `timeline`, and `runbook` all use `_read_events_with_summary()` + `_strict_parse_error()` with shared semantics (`triage_toolkit/cli.py:66-113,116-204`).
   - This closes earlier correctness asymmetry where only parse JSON was guarded.

2. **The main remaining operational bottleneck is eager ingestion**
   - `parse_file_with_summary()` still does `Path.read_text(...).splitlines()` (`triage_toolkit/parser.py:183-185`), which scales memory with full file size.
   - For incident-sized logs, this is the most direct reliability risk (memory pressure / failure before useful output).

3. **UTC canonicalization is correct, but source-timezone provenance is currently dropped from machine output**
   - Canonical UTC normalization is enforced in timestamp parsing (`triage_toolkit/utils.py:17-41`) and appears in timeline/runbook rendering.
   - Parse JSON output currently emits only normalized `timestamp` (`triage_toolkit/models.py:17-24`), with no dedicated `source_timestamp`/`source_offset` fields.
   - This creates downstream compatibility risk for consumers that relied on original offset representation.

4. **Quality gate exists in CI, but confidence headroom is thin and branch distribution is uneven**
   - CI enforces coverage floor (`.github/workflows/ci.yml:27-28`).
   - Current total coverage passes narrowly at 85.46%; `cli.py` remains the weakest area (69%) per local run.
   - Practical implication: one medium refactor can drop below threshold unless targeted tests expand around CLI/file-error branches.

5. **Automation contract is still incomplete**
   - Existing outputs are parser JSON + markdown timeline/runbook (README command surface only: `README.md:39-42`).
   - No dedicated machine-readable incident summary contract yet; this blocks easy integration with ticket enrichers and alert pipelines.

---

## Impact-prioritized roadmap decision

### P0 — ITK-005: Streaming ingestion for large-file safety
**Why now:** highest engineering risk still open; directly tied to operational reliability under real incident volume.

### P1 — ITK-010: Timezone provenance while preserving UTC canonical output
**Why next:** mitigates compatibility fallout from UTC normalization without regressing ordering correctness.

### P1 — ITK-008: Regression matrix expansion + stronger CI confidence margin
**Why third:** coverage floor is already present, but currently near threshold; needs branch-depth expansion before larger feature work.

### P2 — ITK-007: Machine-readable incident summary
**Why later:** high productization value, but should land on stable ingestion + parse contract + stronger regression guardrails.

---

## Assumptions
- Incident logs can be large enough for full-file ingestion to become an operational hazard.
- UTC must remain canonical for ordering/timeline consistency.
- Existing users likely need backward-compatible defaults; strictness should remain opt-in unless explicitly versioned.
- Deterministic outputs are required for CI assertions and downstream automation.

## Unknowns
- No documented performance SLO exists yet (max file size, runtime, memory budget).
- No representative production corpus is available to quantify realistic drop ratios or component/error cardinality.
- No formal parse JSON schema versioning contract exists yet for downstream consumers.
- No clear consumer priority has been provided for summary schema fields beyond current proposal.

## Risks / blockers to monitor
- Streaming refactor can subtly alter newline/encoding/empty-line behavior unless fixture coverage is expanded first.
- Provenance fields can create compatibility churn if schema changes are undocumented or unversioned.
- Raising coverage floor too early may create CI friction; should be coupled to targeted tests and phased upward.
- Summary output can ossify quickly without explicit schema/version policy.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-005 (P0)
2. ITK-010 (P1)
3. ITK-008 (P1)
4. ITK-007 (P2)
