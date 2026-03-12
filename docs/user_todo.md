# user_todo.md

If the AI needs **your** input or manual action, it will add a single checkbox item here and STOP.

- [x] Restore working coding-agent auth for this repo session (the mandated `codex exec --full-auto ...` run failed immediately with `401 Unauthorized: Missing bearer or basic authentication in header` before any repo edits/tests). Verified 2026-03-12 UTC via `codex login status` (`Logged in using an API key - sk-proj-***w1K4A`) and a direct `codex exec --full-auto 'Reply with exactly the word OK and nothing else.'` run that now reaches the API and fails later with quota/billing instead of missing auth.
- [ ] Provide a funded working Codex credential for this session (current state: `codex login status` succeeds with API-key auth, but a direct `codex exec --full-auto 'Reply with exactly the word OK and nothing else.'` reaches the API and fails with `Quota exceeded. Check your plan and billing details.`). After quota/billing is restored or a different working key is supplied, re-run ITK-028 in `/home/node/.openclaw/workspace/projects/auto-senior-pm/repos/incident-triage-toolkit`.
- [x] Approve shell/PTY execution for `incident-triage-toolkit` so the AI can complete exactly one verified milestone and run the required checks (`make lint`, `make test`, plus focused pytest selectors).
