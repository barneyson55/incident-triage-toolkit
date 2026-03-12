Generated: 2026-03-12 UTC  
Repository: `incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays actionable against the live repo state.

## Repo evidence reviewed
- `README.md`
- `docs/AI_EDIT_POLICY.md`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- live file-existence checks for the key docs requested in this pass
- live repo status via `git status --short --branch`
- live source/test footprint checks for `triage_toolkit/`, `tests/`, and `tests/fixtures/`
- focused reads of `triage_toolkit/parser.py`, `triage_toolkit/timeline.py`, and `triage_toolkit/runbook.py`
- focused symbol/test searches across the repo for alias, formatting, and wrapper coverage gaps
- live verification via `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry (`## main...origin/main`)
- `docs/user_todo.md` exists and has no open checkbox items
- current compact repo footprint:
  - 10 source modules under `triage_toolkit/`
  - 11 top-level test modules under `tests/`
  - 18 tracked fixture files under `tests/fixtures/`
  - 174 passing tests in the current collected suite
- live coverage check:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`174 passed`)
  - total coverage: `99%`
  - uncovered lines are now limited to a few thin branches in `triage_toolkit/cli.py` and `triage_toolkit/parser.py`

## Architecture findings from repo evidence

### 1) The top remaining risk is still heterogeneous JSON ingestion drift
Live code review shows `parser.py` still accepts multiple alias families:
- `timestamp | time | ts`
- `level | severity | lvl`
- `component | service | logger`
- `message | msg | event`

It also still resolves correlation IDs by precedence across:
- payload `correlation_id`
- payload `cid`
- message extraction (`cid=` / `correlation_id=`)

Current tests still do **not** directly freeze most of those alias and precedence branches. That makes this the highest-value remaining engineering task because it protects the core heterogeneous-ingestion promise rather than a secondary convenience path.

**Conclusion:** keep **ITK-035 first**.

### 2) The next best gap is CLI-level proof that alias-heavy logs survive normalization end-to-end
Even after adding parser-local tests, the public contract lives in the CLI outputs, not just helper calls. Right now there is no compact fixture proving alias-heavy JSON logs normalize correctly through:
- `triage parse`
- `triage summary`
- `triage timeline`
- `triage runbook`

This deserves to sit immediately after the parser-local task because it converts the heterogeneous-ingestion promise into an end-to-end product contract.

**Conclusion:** add **ITK-037 second**.

### 3) Markdown renderer edge cases are still real, but now clearly third
Focused code review shows:
- `timeline.py` escapes pipe characters for table cells
- `timeline.py` and `runbook.py` flatten embedded newlines before rendering

Those guardrails exist in code, but the tests still do not directly lock them. This is still worth doing because malformed markdown is user-visible and can degrade operator handoffs. It just sits behind the more central ingestion-contract work.

**Conclusion:** keep **ITK-034 active**, but behind the alias-ingestion tasks.

### 4) The remaining uncovered lines are now small wrapper/helper branches, not major semantic gaps
The live coverage report isolates the remaining misses to thin branches such as:
- `_read_stdin_lines()` fallback without `sys.stdin.buffer`
- `_read_events_for_parse([])` guard
- no-filter passthrough in `_apply_event_filters(...)`
- summary file-success echo path
- `main()` wrapper
- `parse_file(...)` wrapper

That is useful cleanup, but it is no longer the best next engineering move while parser alias behavior still lacks direct and end-to-end locking.

**Conclusion:** keep wrapper cleanup last via **ITK-036**.

## Priority conclusions
1. **ITK-035** — direct parser coverage for alias and correlation-ID precedence
2. **ITK-037** — end-to-end CLI contract fixture for alias-shaped JSON logs
3. **ITK-034** — focused markdown formatting edge coverage for timeline/runbook
4. **ITK-036** — close remaining thin wrapper/helper branch gaps

## What changed vs the previous ordering
Previous open queue:
1. ITK-035
2. ITK-034

Refreshed queue:
1. ITK-035
2. ITK-037
3. ITK-034
4. ITK-036

Meaning:
- **ITK-035 stays first** because the core ingestion-risk assessment still holds up after live repo review.
- **ITK-037 is newly added** because the repo still lacks an end-to-end heterogeneous-JSON alias fixture at the CLI contract layer.
- **ITK-034 moves down one slot** because markdown formatting is important, but parser normalization is more central to the product promise.
- **ITK-036 is added last** to sweep up the thin wrapper/helper branches exposed by the 99% coverage report.
- stale repo-shape language was refreshed to match the live suite state (`174 passed`, `99%` coverage, 18 fixture files).

## Risks / blockers to watch
- **Task overlap risk:** ITK-035 and ITK-037 should stay complementary. Keep ITK-035 parser-local and ITK-037 CLI-contract-focused instead of duplicating assertions across both.
- **Golden-test sprawl:** ITK-037 and ITK-034 should prefer compact fixtures and narrow assertions over broad golden churn.
- **Wrapper-cleanup temptation:** ITK-036 is intentionally last. Do not let easy branch coverage displace the more important heterogeneous-ingestion work.
- **Status-doc drift:** this pass intentionally refreshed planning docs only; `docs/status.md` was not edited in this maintenance pass.

## Why this refresh was needed
The prior queue was too short for the requested maintenance posture and underrepresented the current repo state. After a live 99%-coverage verification pass, the highest-value work is clearer:
- first lock heterogeneous JSON alias behavior locally
- then prove it end-to-end at the CLI surface
- then finish markdown edge assertions
- finally sweep the remaining thin wrapper branches
