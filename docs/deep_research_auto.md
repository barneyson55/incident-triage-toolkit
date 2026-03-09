# deep_research_auto.md

Generated: 2026-03-09 16:57 UTC  
Repository: `incident-triage-toolkit`  
Scope: refresh the docs-only engineering priority order so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `README.md`
- `pyproject.toml`
- `triage_toolkit/{cli.py,models.py,parser.py,runbook.py,timeline.py}`
- `tests/{test_cli.py,test_parser.py,test_runbook.py,test_timeline.py}`

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`85 passed`)

## Live architecture snapshot
1. **The core CLI baseline is healthy**
   - Multi-input ingestion, deterministic merge order, dropped-line diagnostics, filter parity, and stdin ingestion are all now shipped and documented.
   - The repo is no longer bottlenecked on basic command-surface parity.

2. **The biggest remaining product gap is the runbook output itself**
   - `triage_toolkit/runbook.py` still produces a mostly boilerplate template with a thin symptom header.
   - For real support handoff value, the next highest-leverage step is evidence-rich markdown, not more plumbing.

3. **There is now a real semantic drift between JSON and markdown outputs**
   - `triage_toolkit/cli.py::_build_incident_summary()` counts error events only when `event.level.upper() == "ERROR"`.
   - `triage_toolkit/timeline.py::is_error()` (used by timeline + runbook) also treats `CRITICAL`, `FATAL`, and message-level `error` hints as evidence.
   - That means the same incident can produce conflicting JSON vs markdown interpretations.

4. **Multi-input provenance is still incomplete for successful events**
   - Dropped-line diagnostics preserve `source_path` and `line_number`, but successful parsed events do not.
   - This weakens auditability and makes rich runbook evidence harder to trace back to the original source line.

5. **Richer evidence will increase safe-sharing pressure**
   - The toolkit already exposes raw dropped lines when diagnostics are enabled.
   - If richer evidence excerpts are added next, the product should offer deterministic redaction rather than depend entirely on upstream manual scrubbing.

## Roadmap decisions derived from the current repo

### P1 — ITK-017: Make runbook output evidence-driven
**Why now:** highest user-visible product gap after the parser/CLI groundwork is complete.

### P1 — ITK-019: Unify incident evidence semantics across `summary`, `timeline`, and `runbook`
**Why next:** once the runbook grows stronger, conflicting error logic between JSON and markdown becomes a trust problem.

### P1 — ITK-020: Preserve source provenance for successful parsed events and rendered evidence
**Why third:** multi-input value is materially higher when every evidence row can be traced back to its source file/stdin label and original line.

### P2 — ITK-021: Add deterministic redaction controls for diagnostics and evidence surfaces
**Why later:** this becomes more important as evidence surfaces become richer, but it should build on the upgraded output contracts above.

## Explicitly de-prioritized in this pass
- Broad parser-format expansion: still not strongly justified by the small bundled sample corpus.
- More foundational CLI plumbing: current command coverage and tests are already strong.
- Non-doc source changes: out of scope for this maintenance pass.

## Risks / blockers to monitor
- Evidence-driven runbook work can fork the analysis model if it does not reuse shared helpers.
- Adding provenance changes the parse contract and will require careful schema-version discipline.
- Built-in redaction must be documented as best-effort rather than perfect secrecy.
- Future maintenance passes should not rely on stale pre-ITK-016 / pre-ITK-018 research notes.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-017 — evidence-driven runbook
2. ITK-019 — unified evidence semantics
3. ITK-020 — source provenance for successful events
4. ITK-021 — deterministic redaction controls
