# deep_research_auto.md

Generated: 2026-03-09 08:41 UTC  
Repository: `incident-triage-toolkit`  
Scope: architecture/roadmap deep-research pass to keep `docs/ai_todo.md` continuously actionable and impact-prioritized.

## Method

### Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/user_todo.md`
- `README.md`
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `Makefile`
- `triage_toolkit/{cli.py,parser.py,models.py,timeline.py,runbook.py,utils.py,__main__.py}`
- `tests/{test_cli.py,test_parser.py,test_timeline.py,test_runbook.py,test_utils.py,test_main.py}`
- `samples/{app.log,app.jsonl,http.log}`
- working-tree diff for `README.md`, `tests/test_cli.py`, and `triage_toolkit/cli.py`

### Local verification run
- `git status --short` ⚠️ working tree not clean; active non-doc edits already exist in `README.md`, `tests/test_cli.py`, and `triage_toolkit/cli.py`
- `make test` ✅ (65 passed)
- `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and multiple_inputs"` ✅ (3 passed)
- `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=88` ✅ (98.01%)

### Minimal external validation used
- JSON Lines guidance: line-oriented data should be processable one record at a time and works well with shell pipelines/log files — supports prioritizing stdin-friendly ergonomics. Source: https://jsonlines.org/
- Semantic Versioning 2.0.0: backward-compatible contract additions should map to MINOR bumps; incompatible machine-readable contract changes should map to MAJOR bumps. Source: https://semver.org/

---

## Architecture snapshot (repo-grounded)

1. **The core pipeline is now stable and well-tested**
   - `parser.py` handles ingestion + normalization.
   - `timeline.py` and `runbook.py` render over normalized events.
   - `cli.py` owns command wiring, strict parse gates, summary assembly, and output writing.
   - Current verification is strong (`65 passed`, `98.01%` coverage), so the next roadmap should optimize operator usability and explainability, not foundational correctness.

2. **The old highest-priority parity gap is already closed in the working tree**
   - Local changes in `triage_toolkit/cli.py`, `tests/test_cli.py`, and `README.md` show `triage summary` now accepts multiple input paths and is covered by focused tests.
   - That means `docs/status.md` is now a lagging snapshot rather than the best reflection of repo reality.
   - Result: ITK-014 should move out of the open queue and the next bottleneck becomes post-parse explainability.

3. **Strict parse quality is strong, but failure explainability is weak**
   - Parse/timeline/runbook/summary now have good deterministic behavior and quality gates.
   - Operators still only get aggregate drop counts and reason buckets.
   - The highest-confidence next product improvement is a deterministic, bounded dropped-line diagnostics surface.

4. **The highest remaining workflow leverage is operator ergonomics**
   - Filtering by component/level/correlation ID would remove a lot of manual shell work for noisy incidents.
   - Stdin support would unlock the natural operating mode for a line-oriented CLI (`kubectl logs`, `journalctl`, pasted snippets, pipeline transforms).
   - Both of these improve day-2 usage more than adding another internal-quality meta-task.

5. **Runbook enrichment is valuable, but should consume stabilized evidence surfaces**
   - The runbook is already deterministic and useful as a starter template.
   - Once diagnostics/filtering/input ergonomics are settled, runbook sections can be upgraded with stronger evidence without duplicating business logic.
   - Sequencing runbook enrichment after those surfaces reduces churn in markdown contract design.

6. **Broad parser-format expansion is still not evidence-backed**
   - The repo contains only a small representative sample corpus.
   - There is still no stored production corpus showing that key-value logs, multiline stack traces, or nested JSON payloads are the most urgent next step.
   - Expanding format support now would be more speculative than improving diagnostics and ergonomics.

---

## Roadmap decisions derived from the evidence

### P1 — ITK-015: Add deterministic dropped-line diagnostics
**Why now:** the toolkit already prevents silent parse loss, but it still does not explain rejected input well enough for high-trust incident use.

### P1 — ITK-016: Add deterministic incident-slicing filters
**Why next:** filtering by component/level/correlation ID is the cleanest operator-ergonomics improvement visible from the current command surface.

### P1 — ITK-018: Support stdin ingestion (`-`)
**Why third:** JSONL-style, line-oriented tooling is strongest when it works naturally in shell pipelines. This improves all command surfaces, not just one output.

### P2 — ITK-017: Enrich runbook output with stronger evidence
**Why later:** worthwhile for handoffs and RCA starts, but it should follow the diagnostics/filter/input work so the markdown contract builds on settled analysis rules.

### Explicit deferral: broad parser-format expansion
**Reason to defer:** current repo evidence still does not justify which additional log shapes matter most, so parser widening would be guesswork-heavy.

---

## Assumptions
- Multi-file incident handling is already materially solved locally by the ITK-014 working-tree changes.
- Operators care most about deterministic outputs, debuggable failures, and shell-friendly workflows.
- UTC should remain canonical while source-time provenance stays additive.
- Machine-readable contract changes should follow explicit versioning discipline.
- The repo is mature enough that the next gains come from usability and trust, not basic test scaffolding.

## Unknowns
- No representative production log corpus is stored in the repo beyond small samples/fixtures.
- No documented redaction policy exists yet for exposing raw dropped lines in diagnostics.
- No final decision exists yet on whether diagnostics should live inside parse output or behind a dedicated command/flag.
- No formal ranking exists between filter types beyond the obvious first wave (`component`, `level`, `correlation_id`).
- No explicit stdin source-labeling convention is documented yet for mixed file + stdin runs.

## Risks / blockers to monitor
- `docs/status.md` is stale relative to the verified working tree and could mislead the next maintenance pass if treated as canonical.
- There are already active local source edits in progress; future doc refreshes should avoid assuming a clean baseline.
- Dropped-line diagnostics can expose sensitive raw text unless bounds/redaction rules are written first.
- Filters must not weaken strict parse semantics by evaluating only the filtered subset.
- Stdin support needs deterministic ordering and labeling rules when mixed with file inputs.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-015 — dropped-line diagnostics
2. ITK-016 — deterministic filters
3. ITK-018 — stdin ingestion
4. ITK-017 — evidence-rich runbook
