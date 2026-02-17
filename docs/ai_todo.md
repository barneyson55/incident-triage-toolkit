# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current repo verification (2026-02-17 15:31 UTC):
- `make test` ✅ (47 passed)
- `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=88` ✅ (98.24%; `triage_toolkit/cli.py` at 98%)

## Open priorities (highest engineering impact first)

- [ ] ITK-010 (P1): Preserve timezone provenance while keeping UTC as canonical output
  - Why (impact): UTC normalization fixed ordering, but downstream consumers may still need original source offset/timestamp context for audit and correlation.
  - DoD:
    - Keep canonical UTC `timestamp` unchanged in parse output.
    - Add deterministic provenance fields in parse events (e.g., `source_timestamp`, `source_offset`) for both JSON and text log inputs.
    - Keep timeline/runbook rendering UTC-first and unaffected by provenance additions.
    - Document parse-event schema changes and backward-compatibility expectations in README.
  - Verification:
    - `pytest -q tests/test_parser.py -k "provenance or source_offset or source_timestamp"`
    - `pytest -q tests/test_cli.py -k "parse and provenance and timezone"`
    - `pytest -q tests/test_timeline.py -k "utc"`
    - `make lint && make test`

- [ ] ITK-007 (P2): Add machine-readable incident summary output for automation
  - Why (impact): current outputs are human-friendly but weak for ticket enrichment and alert pipeline integration.
  - DoD:
    - Add deterministic summary output surface (new command or option) with keys: incident window, event count, error count, top components, top error signatures, correlation-id coverage.
    - Include `schema_version` and document stability/ordering guarantees in README.
    - Ensure summary timestamps are UTC-normalized.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary or schema_version"`
    - `pytest -q tests/test_timeline.py -k "signature"`
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
