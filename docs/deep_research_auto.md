Generated: 2026-03-11 16:58 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `README.md`
- `pyproject.toml`
- `triage_toolkit/{cli.py,evidence.py,models.py,parser.py,runbook.py,timeline.py}`
- `tests/{test_cli.py,test_parser.py,test_runbook.py,test_timeline.py}`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists

## Local verification run
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`98 passed`)

## Minimal external validation
- Python official sorting docs state that Python sort is **stable** (equal-key items preserve input order). That explains why the current timestamp-only helper ordering behaves deterministically in existing CLI flows, but it also highlights that the repo is still relying on an implementation property instead of an explicit product-level tie-break contract.
- SemVer 2.0.0 guidance says **minor** versions are for backward-compatible new functionality. That matches the current summary schema bump to `1.1.0` for additive `evidence_by_source` output.

## Live architecture snapshot
1. **The CLI ingestion pipeline is centralized and healthy**
   - `triage_toolkit/cli.py` funnels `parse`, `summary`, `timeline`, and `runbook` through shared ingestion helpers, strict parse gates, and common filter semantics.
   - This is good news: the product is no longer missing basic command parity, and the remaining work is mostly contract hardening and output parity.

2. **Successful-event provenance is already shipped end-to-end**
   - `triage_toolkit/models.py` now carries `source_timestamp`, `source_offset`, `source_path`, and `line_number`.
   - `triage_toolkit/parser.py` stamps successful parsed events with stable source labels and line numbers.
   - `tests/test_parser.py` and `tests/test_cli.py` already lock those provenance expectations.
   - Conclusion: the old traceability gap is closed. It should not stay near the top of the queue anymore.

3. **Per-source evidence concentration is only half-finished**
   - `triage_toolkit/evidence.py` already exposes `build_source_evidence()` / `evidence_by_source()`.
   - `triage_toolkit/cli.py` already ships `evidence_by_source` in `triage summary` with `SUMMARY_SCHEMA_VERSION = "1.1.0"`.
   - `triage_toolkit/timeline.py` and `triage_toolkit/runbook.py` still show per-event provenance, but they do not yet summarize which source dominates the incident slice.
   - Conclusion: ITK-022 should stay first, but only the remaining human-readable parity work.

4. **The determinism gap has moved from merge logic to helper-layer explicitness**
   - `cli.py::_read_events_for_parse()` explicitly sorts merged events by `(timestamp, source_index, event_index)`.
   - `evidence.py::order_events()` still sorts only by `event.timestamp`.
   - In practice, current CLI flows remain deterministic because merged input is already ordered and Python sort is stable, but that guarantee is indirect and fragile as a product contract.
   - Conclusion: the next highest-value hardening step is making the same-timestamp tie-break rule explicit across all downstream helper paths.

5. **`triage summary` is now a real API surface and needs stronger contract locking**
   - The repo already has rich summary assertions in `tests/test_cli.py`, including multi-input, stdin, filter, and ordering behavior.
   - What is still missing is the same style of dedicated golden/contract fixture coverage that already exists for parse/timeline/runbook outputs.
   - Conclusion: once ITK-022/ITK-023 land, summary JSON contract locking is the next leverage point.

## Assumptions
- The current clean working tree plus `98 passed` is the live baseline to prioritize from.
- README compatibility notes are treated as the intended public contract, not just informal commentary.
- The main supported consumption surfaces remain: human-readable markdown (`timeline`, `runbook`) and machine-readable JSON (`parse`, `summary`).

## Unknowns
- Whether timeline/runbook source concentration should render the top N sources only or all ranked sources.
- Whether explicit equal-timestamp tie-break data should live on `LogEvent` itself or remain a helper/ordering concern.
- Whether downstream automation consumers care about literal JSON key ordering in `summary` or only semantic shape/content.

## Roadmap decisions derived from the current repo

### P1 — ITK-022: Finish per-source evidence concentration in timeline/runbook
**Why now:** the underlying data and ranking helper already exist, `summary` already exposes the machine-readable version, and the human-facing outputs are the obvious remaining parity gap.

### P1 — ITK-023: Make equal-timestamp determinism explicit across helper paths
**Why next:** the product promise is deterministic ordering, but helper-layer ordering still depends on stable-sort behavior plus preserved caller order rather than one explicit end-to-end contract.

### P2 — ITK-024: Add dedicated golden/contract coverage for summary JSON
**Why after that:** `summary` is already versioned and richer than before, so the right follow-up is to make accidental schema/output drift painfully obvious in tests.

## Explicitly de-prioritized in this pass
- New parser-format expansion: current evidence does not show a stronger need than finishing source parity and determinism hardening.
- Dependency growth or broader refactors: the repo is intentionally lightweight (`typer` only at runtime) and does not need extra moving parts for the current roadmap.
- Reopening provenance/redaction as top-level priorities: both are already shipped and covered enough to move down unless new regressions appear.

## Risks / blockers to monitor
- ITK-022 should reuse shared source-ranking helpers rather than creating separate timeline/runbook ranking rules.
- ITK-023 must preserve the existing documented merge contract (`timestamp`, then CLI input order, then line order) rather than accidentally replacing it with lexical path ordering.
- ITK-024 should lock the current contract without overpromising cosmetic JSON key ordering that external consumers may not truly need.

## Priority mapping reflected in `docs/ai_todo.md`
1. ITK-022 — finish human-readable source concentration parity
2. ITK-023 — make equal-timestamp determinism explicit end-to-end
3. ITK-024 — add dedicated summary JSON golden/contract coverage
