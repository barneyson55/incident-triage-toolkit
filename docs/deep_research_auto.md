Generated: 2026-03-13 UTC  
Repository: `incident-triage-toolkit`  
Repo root reviewed: `/home/node/.openclaw/workspace/projects/auto-senior-pm/repos/incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays aligned with the live repo state.

## Repo evidence reviewed
- `README.md`
- `pyproject.toml`
- `docs/AI_EDIT_POLICY.md`
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- `triage_toolkit/cli.py`
- `triage_toolkit/parser.py`
- `triage_toolkit/timeline.py`
- `triage_toolkit/runbook.py`
- `triage_toolkit/markdown.py`
- `tests/test_cli.py`
- `tests/test_cli_helpers.py`
- `tests/test_main.py`
- live file-existence checks for `docs/status.md`, `docs/critical_todo.md`, `docs/ai_todo.md`, and `docs/deep_research_auto.md`
- live repo status via `git status --short --branch`
- live verification via `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

Missing `status` / `critical_todo` files would have been acceptable per the maintenance brief, but both are present in this repo.

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry (`## main...origin/main`)
- `docs/user_todo.md` exists and has no open checkbox items
- live coverage check:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`188 passed`)
  - total coverage: `99%`
  - uncovered lines are now limited to:
    - `triage_toolkit/cli.py:102,148,264,397,522`
    - `triage_toolkit/parser.py:265-266`
- live file structure still confirms a deliberately small package with one direct runtime dependency (`typer==0.21.1`) and dense direct coverage already in place for parser, evidence, redaction, summary-contract, timeline, runbook, and parity behavior

## Evidence-based roadmap conclusions
### 1) `ITK-034` is done; stop treating markdown pipe/newline hardening as open work
`docs/status.md` now shows the pipe/newline milestone completed, including:
- shared `triage_toolkit/markdown.py`
- timeline/runbook renderer updates
- focused regression tests for newline/pipe-heavy dynamic fields

Conclusion:
- previous roadmap notes that still positioned `ITK-034` as the next open item were stale and needed correction.

### 2) The highest remaining user-visible gap is now `summary --out <file>` parity
Repo evidence:
- README quickstart documents file-output flows for all commands
- `triage summary` already has stdout/contract coverage
- the summary file-success echo branch in `cli.py` remains uncovered

Conclusion:
- the next task should be a narrow CLI contract test for `triage summary --out <file>` rather than more generic coverage chasing.

### 3) Remaining product-risk work is mostly around operator-facing markdown/code-span safety and real entrypoints
Repo evidence:
- runbook output still embeds several dynamic values inside backticks and a raw `# {title}` heading
- package metadata defines the installed `triage` console script, but current direct subprocess coverage is stronger for `python -m triage_toolkit` than for the installed wrapper
- strict-gate error signaling is covered, but file-output safety on failing strict runs is not directly locked yet

Conclusion:
- after `ITK-038`, the best remaining tasks are contract/surface hardening, not broad parser changes.

### 4) Pure coverage mop-up is real but lower priority now
The last uncovered lines are thin glue only:
- `_read_stdin_lines()` fallback without `.buffer`
- `_read_events_for_parse([])`
- correlation-ID filter miss path in `_apply_event_filters(...)`
- summary write-success echo path
- `triage_toolkit.cli` script entrypoint
- `parse_file(...)`

Conclusion:
- this is worth doing, but only after the remaining user-visible seams are locked.

## Refreshed priority order
1. `ITK-038` — lock `triage summary --out <file>` at the CLI contract layer
2. `ITK-040` — harden remaining runbook markdown/code-span safety for titles/backticks
3. `ITK-039` — lock installed `triage` console-script parity with the documented quickstart
4. `ITK-041` — prove strict parse-gate failures never create or overwrite output files
5. `ITK-036` — finish the remaining thin helper/wrapper seams

## What changed vs the previous research note
- `ITK-034` moved from “next open item” to completed work.
- The queue now stays at 5 concrete open items instead of drifting down to only 2.
- Coverage-only cleanup is intentionally pushed below the remaining user-visible CLI/markdown/entrypoint seams.

## Risks / blockers
- `docs/critical_todo.md` is present and empty (`- (none)`), so there is no critical blocker escalation right now.
- Main planning risk is reverting to vanity coverage work before the remaining documented quickstart/entrypoint/file-safety contracts are locked.
- Console-script smoke tests can become environment-sensitive if implemented carelessly; keep them focused on the active dev install rather than hardcoded paths.
