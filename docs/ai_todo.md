# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current `docs/ai_todo.md` review (2026-02-17 09:12 UTC), incorporating completed ITK-006/ITK-009 and the UTC-compatibility follow-up risk noted in `docs/status.md`.

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

- [x] ITK-006 (P0): Normalize outputs to UTC and accept offset-heavy text logs
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

- [x] ITK-009 (P1): Apply parse-quality gates to `timeline` and `runbook` commands
  - Why (impact): `parse --strict` now protects JSON output, but `timeline`/`runbook` still consume silently dropped lines and can produce confident-looking artifacts from partial input.
  - DoD:
    - Add `--strict` and `--max-drop-ratio <0..1>` to `triage timeline` and `triage runbook` with semantics matching `triage parse`.
    - Reuse the same strict-failure messages (including deterministic `parse_summary`) for all commands.
    - Keep default behavior backward-compatible (strict opt-in only).
  - Verification:
    - `pytest -q tests/test_cli.py -k "timeline_strict or runbook_strict"`
    - `pytest -q tests/test_cli.py -k "drop_ratio and (timeline or runbook)"`
    - `make lint && make test`

- [ ] ITK-008 (P1): Expand regression depth and enforce coverage floor in CI
  - Why (impact): parser/UTC/strict changes are now foundational behavior; without a stronger CI gate, future refactors can regress correctness silently.
  - DoD:
    - Add edge-case fixture matrix (invalid lines, mixed formats, multiline noise, timezone variants, correlation-id extraction variants).
    - Add coverage reporting for `triage_toolkit` and enforce `--cov-fail-under=85` in CI.
    - Ensure parser/timeline/runbook strict+UTC behavior has deterministic assertions in CLI-level tests.
  - Verification:
    - `pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=85`
    - `pytest -q tests/test_cli.py -k "strict or drop_ratio or timezone"`
    - `make lint && make test`

- [ ] ITK-005 (P1): Refactor ingestion to stream line-by-line (large-file safe)
  - Why (impact): current `Path.read_text().splitlines()` loads the full input into memory and is the main scalability limit.
  - DoD:
    - Replace eager full-file reads with streaming iteration while preserving parse order.
    - Preserve current UTF-8 decode and I/O error behavior surfaced by CLI.
    - Add regression coverage validating streaming path on large synthetic input and confirming parse counters/strict-gate outcomes remain correct.
  - Verification:
    - `pytest -q tests/test_parser.py -k "stream or large"`
    - `pytest -q tests/test_cli.py -k "io or utf8 or strict"`
    - `make lint && make test`

- [ ] ITK-010 (P1): Preserve timezone provenance while keeping UTC as canonical output
  - Why (impact): UTC normalization fixed ordering, but it can break downstream consumers that relied on original source offsets.
  - DoD:
    - Keep normalized UTC `timestamp` as the canonical output field.
    - Add deterministic provenance field(s) in parse JSON events for source timezone context (for example `source_timestamp` / `source_offset`).
    - Ensure timeline/runbook outputs remain UTC-first and unaffected by provenance metadata.
    - Document schema and backward-compatibility expectations in README.
  - Verification:
    - `pytest -q tests/test_parser.py -k "provenance or source_offset"`
    - `pytest -q tests/test_cli.py -k "parse and timezone and provenance"`
    - `make lint && make test`

- [ ] ITK-007 (P2): Add machine-readable incident summary output for automation
  - Why (impact): current outputs are human-readable but weak for ticketing/alert enrichment automation.
  - DoD:
    - Add deterministic summary surface (new command or option) with keys: incident window, event count, error count, top components, top error signatures, correlation-id coverage.
    - Keep schema stable/versioned and documented in README.
    - Add CLI tests asserting schema keys, deterministic ordering, and UTC-normalized timestamps in summary output.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary"`
    - `pytest -q tests/test_timeline.py -k "signature"`
    - `make lint && make test`

---

Completed baseline (kept for history):

- [x] ITK-001: Add installable packaging + `triage` console script
- [x] ITK-002: Add CI (GitHub Actions) for lint + tests
- [x] ITK-003: CLI UX improvements (stdout output, file errors, `--version`)
