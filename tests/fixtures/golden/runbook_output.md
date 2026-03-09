# Incident: Golden

## Symptoms
- Incident window: `2025-03-01T10:00:00+00:00` → `2025-03-01T10:00:04+00:00`
- First observed: `2025-03-01T10:00:00+00:00`
- Last observed: `2025-03-01T10:00:04+00:00`
- Evidence events: 2 of 4 total
- Top error signatures: `query failed cid=<id>` (1), `request # for user #` (1)
- Suspected components: db (1), api (1)
- Representative correlation IDs: `q-9`

## Evidence

### Top Error Signatures
- query failed cid=<id> (count: 1, first: 2025-03-01T10:00:02+00:00, last: 2025-03-01T10:00:02+00:00, components: db)
- request # for user # (count: 1, first: 2025-03-01T10:00:04+00:00, last: 2025-03-01T10:00:04+00:00, components: api)

### Example Failures
- `2025-03-01T10:00:02+00:00` `ERROR` `db` — query failed cid=q-9
- `2025-03-01T10:00:04+00:00` `ERROR` `api` — request 500 for user 42

## Checks
- Prioritize health and dependency checks for: db, api.
- Trace these IDs through adjacent logs and traces: q-9.
- Compare the first and last evidence timestamps against deployments or config changes during `2025-03-01T10:00:00+00:00` → `2025-03-01T10:00:04+00:00`.

## Workaround
- Reduce traffic to, disable risky flows in, or otherwise contain the implicated components: db, api.
- Roll back, restart, or fail over the affected service only if that action is consistent with the evidence above.

## Fix/Escalation
- Escalate with the incident window, top signatures, and representative failures captured above: `query failed cid=<id>` (1), `request # for user #` (1).
- Attach the incident timeline and any supporting logs, dashboards, or deployment links needed to reproduce the failure.

## Verification
- Confirm the top signatures stop recurring after mitigation: `query failed cid=<id>` (1), `request # for user #` (1).
- Re-run the critical user flows that touch the implicated components and verify healthy responses.

## Notes
- Add incident-specific decisions, links, owners, and next actions here.
