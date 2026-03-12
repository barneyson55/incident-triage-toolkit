# Incident: Redacted Golden

## Symptoms
- Incident window: `2025-03-02T10:00:00+00:00` → `2025-03-02T10:00:01+00:00`
- First observed: `2025-03-02T10:00:00+00:00`
- Last observed: `2025-03-02T10:00:01+00:00`
- Evidence events: 2 of 2 total
- Top error signatures: `notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1), `timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1)
- Evidence by source: `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log` (2 of 2)
- Suspected components: api (1), worker (1)
- Representative correlation IDs: `[redacted-id:adajebedjhdc]`

## Evidence

### Top Error Signatures
- notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (count: 1, first: 2025-03-02T10:00:00+00:00, last: 2025-03-02T10:00:00+00:00, components: api, example: `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:3`)
- timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (count: 1, first: 2025-03-02T10:00:01+00:00, last: 2025-03-02T10:00:01+00:00, components: worker, example: `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:4`)

### Evidence by Source
- `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log` (evidence: 2 of 2, first: 2025-03-02T10:00:00+00:00)

### Example Failures
- `2025-03-02T10:00:00+00:00` `ERROR` `api` — notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (source: `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:3`)
- `2025-03-02T10:00:01+00:00` `ERROR` `worker` — timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (source: `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:4`)

## Checks
- Prioritize health and dependency checks for: api, worker.
- Trace these IDs through adjacent logs and traces: [redacted-id:adajebedjhdc].
- Compare the first and last evidence timestamps against deployments or config changes during `2025-03-02T10:00:00+00:00` → `2025-03-02T10:00:01+00:00`.

## Workaround
- Reduce traffic to, disable risky flows in, or otherwise contain the implicated components: api, worker.
- Roll back, restart, or fail over the affected service only if that action is consistent with the evidence above.

## Fix/Escalation
- Escalate with the incident window, top signatures, and representative failures captured above: `notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1), `timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1).
- Attach the incident timeline and any supporting logs, dashboards, or deployment links needed to reproduce the failure.

## Verification
- Confirm the top signatures stop recurring after mitigation: `notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1), `timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej]` (1).
- Re-run the critical user flows that touch the implicated components and verify healthy responses.

## Notes
- Add incident-specific decisions, links, owners, and next actions here.
