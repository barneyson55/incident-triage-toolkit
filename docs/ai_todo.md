# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current repo verification (2026-02-17 18:51 UTC):
- `make lint` ✅
- `make test` ✅ (47 passed)
- `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=88` ✅ (98.24%; `cli.py` 98%)

## Open priorities (highest engineering impact first)

- [x] ITK-010 (P1): Preserve timezone provenance while keeping UTC as canonical output
  - Why (impact): UTC normalization fixed ordering, but downstream consumers still need original source offset/timestamp context for audit and cross-system correlation.
  - DoD:
    - Keep canonical UTC `timestamp` unchanged in parse output.
    - Add deterministic provenance fields in parse events (at least `source_timestamp` and `source_offset`) for JSON and text inputs.
    - Keep timeline/runbook rendering UTC-first and unchanged by provenance additions.
    - Document parse-event schema delta and backward-compatibility behavior in README.
  - Verification:
    - `pytest -q tests/test_parser.py -k "provenance or source_offset or source_timestamp"`
    - `pytest -q tests/test_cli.py -k "parse and provenance and timezone"`
    - `pytest -q tests/test_timeline.py -k "utc"`
    - `pytest -q tests/test_runbook.py -k "utc"`
    - `make lint && make test`

- [x] ITK-011 (P1): Version and lock the parse JSON contract before further output expansion
  - Why (impact): upcoming provenance + automation fields increase compatibility risk; a versioned contract prevents silent downstream breakage.
  - Delivered (2026-02-25):
    - Added top-level `schema_version` (`1.0.0`) to `triage parse` JSON payload.
    - Documented additive vs breaking contract rules in README.
    - Added regression coverage for required top-level payload keys and locked event key set.
  - Verification:
    - `pytest -q tests/test_cli.py -k "schema_version or parse_contract"`
    - `pytest -q tests/test_parser.py -k "event_contract or to_dict"`
    - `make lint && make test`

- [x] ITK-007 (P1): Add machine-readable incident summary output for automation
  - Why (impact): current outputs are strong for humans but weak for ticket enrichment, alert pipelines, and programmatic triage handoffs.
  - DoD:
    - Add deterministic summary output surface (new command or option) with keys: incident window, event count, error count, top components, top error signatures, correlation-id coverage.
    - Include `schema_version` and document ordering/stability guarantees in README.
    - Keep all summary timestamps UTC-normalized.
  - Milestones:
    - [x] M1: Added `triage summary` command with deterministic JSON schema (`schema_version`, incident window, counts, top lists, correlation coverage) + CLI regression test.
    - [x] M2: Expand summary-focused tests (`-k "summary or schema_version"`) and harden edge-case behavior.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary or schema_version"`
    - `pytest -q tests/test_timeline.py -k "signature or normalize"`
    - `pytest -q tests/test_runbook.py -k "summary"`
    - `make lint && make test`

- [x] ITK-012 (P2): Add multi-source ingestion (multiple files) with deterministic merge order
  - Why (impact): real incidents usually span multiple log files/services; single-file ingestion increases operator overhead and missed correlation risk.
  - DoD:
    - Allow passing multiple input paths to parse/timeline/runbook flows.
    - Merge events in deterministic global timestamp order (UTC canonical), with deterministic tie-break behavior.
    - Expose per-source parse summary plus aggregate summary in parse output.
    - Document CLI usage and merge semantics in README.
  - Milestones:
    - [x] M1: `triage parse` now accepts multiple input files, merges events by UTC timestamp with deterministic tie-breakers, and emits aggregate + `per_source` parse summary when multi-input is used.
    - [x] M2: Extend multi-input behavior to `timeline` and `runbook`, keeping deterministic merge semantics consistent.
    - [x] M3: Document multi-input CLI usage/merge semantics in README and add focused regression tests for tie-break/per-source summary edges.
  - Verification:
    - `pytest -q tests/test_cli.py -k "multiple_inputs or multi_source"`
    - `pytest -q tests/test_parser.py -k "merge_order or per_source_summary"`
    - `pytest -q tests/test_timeline.py -k "merge or ordering"`
    - `make lint && make test`

- [x] ITK-013 (P2): Add golden-output contract tests for parse/timeline/runbook determinism
  - Why (impact): protects CI confidence and prevents accidental format drift that breaks consumers and incident playbooks.
  - DoD:
    - Add fixture corpus with mixed JSON/text, offsets, malformed lines, and correlation-id variants.
    - Add golden assertions for parse JSON, timeline markdown, and runbook markdown outputs.
    - Ensure deterministic newline/key ordering expectations are explicit in tests.
  - Verification:
    - `pytest -q tests/test_cli.py -k "golden or deterministic"`
    - `pytest -q tests/test_timeline.py -k "golden"`
    - `pytest -q tests/test_runbook.py -k "golden"`
    - `make lint && make test`

---

Completed baseline (kept for history):

- [x] ITK-001: Add installable packaging + `triage` console script
- [x] ITK-002: Add CI (GitHub Actions) for lint + tests
- [x] ITK-003: CLI UX improvements (stdout output, file errors, `--version`)
- [x] ITK-004 (P0): Add parse-quality gate to prevent silent data loss
- [x] ITK-005 (P0): Refactor ingestion to stream line-by-line (large-file safe)
- [x] ITK-006 (P0): Normalize outputs to UTC and accept offset-heavy text logs
- [x] ITK-008 (P0): Expand regression matrix and raise CI confidence margin before new feature work
- [x] ITK-009 (P1): Apply parse-quality gates to `timeline` and `runbook` commands


<!-- ASPM_SWEEP_2026-02-25 -->
## ASPM Sweep 2026-02-25
- [x] Portfolio sweep triage logged on branch `main` (pre-sweep repo state: `clean`).
- [x] First unchecked item in `docs/user_todo.md`: none.
- [x] Top-level unchecked count in `docs/ai_todo.md` at sweep start: 4.
- Next step: Execute the first unchecked top-level item already listed in docs/ai_todo.md.

<!-- ASPM_SWEEP_2026-02-27 -->
## ASPM Sweep 2026-02-27
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items remain.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED until a new `docs/user_todo.md` or `docs/ai_todo.md` unchecked item is added.

## ASPM Sweep 2026-02-27 (09:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: still no open user actions.
- [x] Re-checked `docs/ai_todo.md`: still no unchecked top-level engineering items.
- [x] Verification run completed again: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (10:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (11:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (12:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (13:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (14:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (15:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (16:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (17:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (18:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (19:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (20:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (21:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.

## ASPM Sweep 2026-02-27 (22:52 UTC run)
- [x] Re-checked `docs/user_todo.md`: no open user actions.
- [x] Re-checked `docs/ai_todo.md`: no unchecked top-level engineering items.
- [x] Verification run completed: `make test` (63 passed).
- Next step: BLOCKED pending a new unchecked item in `docs/user_todo.md` or `docs/ai_todo.md`.
