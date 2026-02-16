# ASPM Sellable Delivery Scope — 2026-02-16 (wave2)

Repository: `incident-triage-toolkit`

This wave adds a **client-ready delivery scope card** so this project can be sold as a scoped implementation package immediately.

## Docs/TODOs inspected
- `README.md`
- `docs/ai_todo.md`
- `docs/user_todo.md`
- `docs/aspm_ai_todo_2026-02-16.md`
- `docs/critical_todo.md`
- `docs/status.md`

## Concrete improvement delivered in this commit
A productized **Delivery Scope Card** with:
1. Offer framing (what is sold in a fixed scope)
2. Acceptance checklist (definition of done)
3. Demo + handoff flow for buyer confidence
4. Backlog anchors tied to currently visible TODO/STATUS items

### Offer framing
Deliver an operations-safe Python increment with parse/lint/test guardrails and handoff scope.

### Acceptance checklist
- [ ] pyproject.toml parses cleanly with standard tooling.
- [ ] A repo-appropriate smoke/lint/test command is captured.
- [ ] Open TODO items are mapped to sellable milestones.

### Demo & handoff flow
- python3 -m venv .venv && source .venv/bin/activate
- Run repo smoke/lint/test command
- Walk through milestone and acceptance criteria docs

### Backlog anchors from inspected docs
- Quickly normalize mixed logs into a single timeline.
- Identify error patterns and suspected components faster.
- Produce a consistent runbook skeleton for handoffs and follow-ups.
- triage parse <path> --out parsed.json
- triage timeline <path> --out timeline.md
- triage runbook <path> --out runbook.md --title "Incident: ..."
