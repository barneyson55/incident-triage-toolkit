# deep_research_auto.md

Generated: 2026-03-09 18:34 UTC  
Repository: `incident-triage-toolkit`  
Scope: refresh the docs-only engineering priority order so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `README.md`
- `pyproject.toml`
- `triage_toolkit/{cli.py,evidence.py,models.py,parser.py,runbook.py,timeline.py}`
- `tests/{test_cli.py,test_parser.py,test_runbook.py,test_timeline.py}`

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`91 passed`)

## Live architecture snapshot
1. **The core CLI baseline is healthy**
   - Multi-input ingestion, deterministic merge order, dropped-line diagnostics, filter parity, stdin ingestion, richer runbook evidence, and shared error/evidence semantics are now shipped.
   - The repo is no longer bottlenecked on basic command-surface parity.

2. **The biggest remaining trust gap is source traceability**
   - `triage_toolkit/models.py` still does not preserve `source_path` / `line_number` for successful parsed events.
   - Dropped-line diagnostics already preserve provenance, so the success path is now the weaker audit surface.
   - Timeline/runbook output therefore cannot point operators back to the original line that produced a normalized evidence row.

3. **Safe-sharing is still missing where the product is becoming more useful**
   - The toolkit already exposes raw dropped lines when diagnostics are enabled.
   - Runbook evidence/examples are now richer too.
   - That makes deterministic redaction the next real operational hardening step, not just a nice-to-have.

4. **Multi-input support is shipped, but source-level insight is still absent**
   - The product can merge multiple logs deterministically, yet the outputs still emphasize components more than source concentration.
   - Once successful-event provenance lands, the next leverage point is showing which source file/stdin stream dominates the evidence slice.

5. **Two contract surfaces still need explicit hardening before more output growth**
   - End-to-end equal-timestamp determinism is partly implicit outside the CLI merge path.
   - `triage summary` is the main machine-readable automation surface, but it still lacks dedicated contract/golden coverage for the next schema/output expansions.

## Roadmap decisions derived from the current repo

### P1 — ITK-020: Preserve source provenance for successful parsed events and rendered evidence
**Why now:** highest operator-trust and auditability gap in the live repo.

### P1 — ITK-021: Add deterministic redaction controls for diagnostics and evidence surfaces
**Why next:** richer evidence is increasingly shareable only if the toolkit offers a stable safe-sharing mode.

### P2 — ITK-022: Surface per-source evidence concentration across summary/timeline/runbook
**Why after provenance:** source-focused triage becomes much more valuable once successful events carry stable source labels and line numbers.

### P2 — ITK-023: Make equal-timestamp determinism explicit across parse, timeline, runbook, and evidence helpers
**Why next:** determinism is part of the product promise and should be proven, not just implied by current implementation details.

### P2 — ITK-024: Add golden/contract coverage for the summary JSON automation surface
**Why next:** upcoming provenance/source/redaction work will otherwise raise accidental contract-drift risk on the machine-readable path.

## Explicitly de-prioritized in this pass
- Broad parser-format expansion: still not strongly justified by the small bundled sample corpus.
- New non-doc source work in this maintenance pass: out of scope here; only the queue was refreshed.
- Cosmetic doc-only cleanup that does not change engineering leverage.

## Risks / blockers to monitor
- Provenance adds parse-contract surface area, so schema-version discipline matters.
- Redaction must be documented as best-effort, not perfect secrecy.
- Source-level evidence ranking should not fork from the shared evidence semantics that ITK-019 just stabilized.
- Determinism work should avoid accidental regression in the current file/stdin merge contract.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-020 — source provenance for successful events and evidence
2. ITK-021 — deterministic redaction controls
3. ITK-022 — per-source evidence concentration
4. ITK-023 — explicit equal-timestamp determinism contract
5. ITK-024 — summary JSON contract/golden coverage
