# deep_research_auto.md

Generated: 2026-02-16 23:05 UTC  
Repository: `incident-triage-toolkit`  
Scope: architecture/roadmap deep-research pass to keep `docs/ai_todo.md` continuously actionable and impact-prioritized.

## Method

### Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md`
- `README.md`
- `triage_toolkit/{cli.py,parser.py,utils.py,timeline.py,runbook.py,models.py}`
- `tests/{test_cli.py,test_parser.py,test_timeline.py,test_runbook.py}`
- `.github/workflows/ci.yml`
- `Makefile`

### Baseline verification run
- `make lint` ✅
- `make test` ✅ (7 passed)

### Minimal external validation used
- JSON Lines requirements (UTF-8, one valid JSON value per line): https://jsonlines.org/
- RFC 3339 timestamp profile for UTC/offset semantics: https://www.rfc-editor.org/rfc/rfc3339
- `pytest-cov` supports `--cov-fail-under` for CI gating: https://pytest-cov.readthedocs.io/en/stable/config.html
- Typer CLI testing baseline with `CliRunner`: https://typer.tiangolo.com/tutorial/testing/

---

## Architecture snapshot (repo-grounded)

1. **Parser silently drops lines with no quality telemetry**
   - `parse_line()` returns `None` for blank/unparseable lines (`triage_toolkit/parser.py:92-100`).
   - `parse_file()` appends only parsed events; dropped lines are not counted/reported (`triage_toolkit/parser.py:103-110`).
   - Operational effect: output can look “valid” while being materially incomplete.

2. **Timestamp handling is internally capable but externally inconsistent**
   - `parse_timestamp()` can parse ISO timestamps and offsets (`triage_toolkit/utils.py:18-41`).
   - Text-log regex currently allows only `...Z?` suffix, not `+02:00` / `-05:00` (`triage_toolkit/parser.py:15`).
   - Timeline table labels times as UTC while emitting raw `isoformat()` values (`triage_toolkit/timeline.py:44, 51`), and runbook does similar for first-seen (`triage_toolkit/runbook.py:18`).

3. **Ingestion is eager (full-file read) rather than streaming**
   - `Path.read_text(...).splitlines()` loads complete input before parsing (`triage_toolkit/parser.py:106`).
   - Risk rises with incident-scale logs (memory spikes and poorer resilience).

4. **Automation surface is thin**
   - CLI offers parse/timeline/runbook (`triage_toolkit/cli.py:79-116`), but no dedicated machine-readable incident summary contract.
   - This limits immediate integrations (ticket enrichers, alerts, dashboards).

5. **Quality envelope is currently minimal**
   - 7 tests total across parser/cli/timeline/runbook.
   - CI runs lint + pytest only, with no coverage floor (`.github/workflows/ci.yml`).

---

## Impact-prioritized roadmap decision

### P0 — ITK-004: Parse-quality gate (silent-loss prevention)
**Why now:** highest correctness risk; prevents false confidence in downstream timeline/runbook outputs.

### P0 — ITK-006: UTC normalization + offset-heavy text-log support
**Why moved up:** incident sequencing correctness is core value. Current “UTC” labeling can mislead when mixed offsets exist.

### P1 — ITK-005: Streaming ingestion (large-file safety)
**Why:** reliability/performance for realistic incident artifacts; should follow core correctness guardrails.

### P1 — ITK-008: Regression depth + CI coverage floor
**Why moved ahead of summary:** protects parser/timestamp/streaming refactors before expanding feature surface.

### P2 — ITK-007: Machine-readable incident summary output
**Why later:** high integration value, but should sit on a hardened parse/time/test foundation.

---

## Assumptions
- Real incident logs are heterogeneous and can include mixed timezone offsets.
- Users likely prefer backward-compatible defaults unless strict behavior is explicitly requested.
- Deterministic CLI output is required for automation and stable tests.

## Unknowns
- No representative production corpus is available to quantify typical drop ratios.
- No documented performance SLO (file size / runtime / memory envelope) exists.
- No formal consumer contract yet for summary JSON schema.
- Coverage threshold target (e.g., 75/80/85%) is not yet policy-defined.

## Risks / blockers to monitor
- Strict parsing may break existing scripts if defaults are changed abruptly.
- UTC normalization will change rendered fixtures and may require broad test updates.
- Streaming refactor can alter edge-case newline/encoding behavior without regression depth.
- Coverage gating may initially fail CI until legacy gaps are closed or threshold is phased.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-004 (P0)
2. ITK-006 (P0)
3. ITK-005 (P1)
4. ITK-008 (P1)
5. ITK-007 (P2)
