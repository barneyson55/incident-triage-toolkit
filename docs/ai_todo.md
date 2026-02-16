# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/deep_research_auto.md` (2026-02-16 23:05 UTC).

- [x] ITK-004 (P0): Add parse-quality gate to prevent silent data loss
  - Why (impact): parser currently drops unparseable lines silently; triage output can look valid while being incomplete.
  - DoD:
    - Add parse quality counters (`total_lines`, `parsed_lines`, `dropped_lines`) and dropped-reason buckets.
    - Add `triage parse --strict` and `--max-drop-ratio <0..1>` (default remains backward-compatible / non-strict).
    - In strict mode, return non-zero exit code when `parsed_lines == 0` or drop ratio exceeds threshold.
    - Emit parse summary in a deterministic structure suitable for test assertions.
  - Verification:
    - `pytest -q tests/test_parser.py -k "stats or dropped"`
    - `pytest -q tests/test_cli.py -k "strict or drop_ratio"`
    - `make lint && make test`

- [ ] ITK-006 (P0): Normalize outputs to UTC and accept offset-heavy text logs
  - Why (impact): timeline labels times as UTC, but text-log parsing and emitted timestamps can currently preserve mixed offsets.
  - DoD:
    - Extend text-log timestamp parsing to accept RFC3339-style offsets (`+HH:MM`, `-HH:MM`) in addition to `Z`.
    - Normalize emitted timestamps to UTC across parse JSON, timeline, and runbook outputs.
    - Add mixed-offset regression coverage (`Z`, `+02:00`, `-05:00`) for ordering + rendered output.
  - Verification:
    - `pytest -q tests/test_parser.py -k "timezone or offset"`
    - `pytest -q tests/test_timeline.py -k "utc or timezone"`
    - `pytest -q tests/test_runbook.py -k "utc or timezone"`
    - `make lint && make test`

- [ ] ITK-005 (P1): Refactor ingestion to stream line-by-line (large-file safe)
  - Why (impact): current `Path.read_text().splitlines()` loads the full input into memory.
  - DoD:
    - Replace full-file read with streaming iteration while preserving parse order.
    - Preserve current UTF-8 + I/O error semantics in CLI.
    - Add regression test on large synthetic input to validate correctness under streaming path.
  - Verification:
    - `pytest -q tests/test_parser.py -k "stream or large"`
    - `pytest -q tests/test_cli.py -k "io or utf8"`
    - `make lint && make test`

- [ ] ITK-008 (P1): Expand regression depth and enforce coverage floor in CI
  - Why (impact): parser/UTC/streaming changes widen regression surface beyond current 7 tests.
  - DoD:
    - Add edge-case fixture matrix (invalid lines, mixed formats, multiline noise, timezone variants).
    - Add coverage reporting for `triage_toolkit` and enforce a minimum threshold in CI (via `pytest-cov` / fail-under).
    - CI must fail when coverage is below threshold.
  - Verification:
    - `pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=<threshold>`
    - GitHub Actions CI run shows expected pass/fail behavior for coverage gate.
    - `make lint && make test`

- [ ] ITK-007 (P2): Add machine-readable incident summary output for automation
  - Why (impact): current outputs are human-readable but weak for ticketing/alert enrichment automation.
  - DoD:
    - Add deterministic summary surface (new command or option) with keys: incident window, event count, error count, top components, top error signatures, correlation-id coverage.
    - Keep schema stable and documented in README.
    - Add CLI tests asserting schema keys and deterministic ordering.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary"`
    - `pytest -q tests/test_timeline.py -k "signature"`
    - `make lint && make test`

---

Completed baseline (kept for history):

- [x] ITK-001: Add installable packaging + `triage` console script
- [x] ITK-002: Add CI (GitHub Actions) for lint + tests
- [x] ITK-003: CLI UX improvements (stdout output, file errors, `--version`)
