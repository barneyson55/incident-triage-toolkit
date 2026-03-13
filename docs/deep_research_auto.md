Generated: 2026-03-13 UTC  
Repository: `incident-triage-toolkit`  
Repo root reviewed: `/home/node/.openclaw/workspace/projects/auto-senior-pm/repos/incident-triage-toolkit`  
Scope: docs-only priority refresh so `docs/ai_todo.md` stays aligned with the live repo state.

## Repo evidence reviewed
- `docs/status.md`
- `docs/critical_todo.md`
- `docs/ai_todo.md` (pre-refresh)
- `docs/deep_research_auto.md` (pre-refresh)
- `docs/user_todo.md`
- `README.md`
- `docs/AI_EDIT_POLICY.md`
- live file-existence checks for `docs/status.md`, `docs/critical_todo.md`, `docs/ai_todo.md`, and `docs/deep_research_auto.md`
- live repo status via `git status --short --branch`

## Docs file existence check
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists

Missing `status` / `critical_todo` files would have been acceptable per the maintenance brief, but both are present in this repo.

## Live repo snapshot used for reprioritization
- `git status --short --branch` showed a clean tree on entry (`## main...origin/main`)
- `docs/user_todo.md` exists and has no open checkbox items
- `docs/status.md` is the current source of truth for the last green verification:
  - `make lint` ✅
  - `make test` ✅ (`197 passed`)
- `docs/critical_todo.md` is present and currently empty (`- (none)`)

## Evidence-based roadmap conclusions

### 1) ITK-041 is complete and should not stay in the active queue
`docs/status.md` now records the strict parse-gate file-safety milestone as done, including focused CLI regressions that prove failed `--strict --out <file>` runs do not create fresh outputs or overwrite sentinel files.

Conclusion:
- strict-mode output-file safety is no longer an open planning priority.

### 2) ITK-038 is also complete, so summary file-output parity is already locked
`docs/status.md` records the README-advertised `triage summary --out <file>` path as complete and verified.

Conclusion:
- the active queue should stop carrying summary write-path parity as an open item.

### 3) The highest remaining engineering risk is still operator-facing runbook markdown safety
The live docs state that pipe/newline corruption is fixed, but the remaining open item still points at literal backticks and embedded newlines inside runbook titles and inline-code fields.

Conclusion:
- ITK-040 should remain the first unchecked top-level task.

### 4) After markdown safety, the remaining work is entrypoint parity and tiny intentional coverage seams
With no critical blockers queued, the remaining queue should stay short and concrete:
- installed `triage` console-script parity with the README quickstart
- direct coverage for the last thin helper/wrapper/entrypoint branches

Conclusion:
- ITK-039 should stay ahead of ITK-036 because it protects first-run user experience rather than only coverage neatness.

## Refreshed priority order
1. `ITK-040` — harden remaining runbook markdown/code-span safety for titles/backticks/newlines
2. `ITK-039` — lock installed `triage` console-script parity with the documented quickstart
3. `ITK-036` — close the remaining thin helper/wrapper seams so the last uncovered lines are intentional

## What changed vs the previous research note
- Removed stale open-priority treatment of `ITK-038` and `ITK-041`; both are completed in `docs/status.md`.
- Reduced the live queue to 3 concrete open items so it stays actionable instead of mixing completed and open work.
- Kept the queue ordered by user-visible risk first, coverage mop-up last.

## Risks / blockers
- `docs/critical_todo.md` is present and empty (`- (none)`), so there is no critical blocker escalation right now.
- Main planning risk is letting completed milestones linger near the top of `docs/ai_todo.md`, which makes the deterministic “first unchecked top-level item” workflow noisier than it needs to be.
- `ITK-039` can be implemented badly if the test hardcodes an environment-specific script path; keep it virtualenv-aware and narrow.
