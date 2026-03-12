# Incident Timeline

T0: `2025-03-02T10:00:00+00:00`

## Events

| Time (UTC) | Source | Level | Component | Message |
| --- | --- | --- | --- | --- |
| 2025-03-02T10:00:00+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:3 | ERROR | api | notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] |
| 2025-03-02T10:00:01+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log:4 | ERROR | worker | timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] |

## Notable Errors
- notify [redacted-email:ffidjibjfcae] from [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (count: 1, first: 2025-03-02T10:00:00+00:00, last: 2025-03-02T10:00:00+00:00)
- timeout [redacted-email:ffidjibjfcae] at [redacted-ip:deadegbafcag] cid=[redacted-id:adajebedjhdc] [redacted-secret:cgdhbhaafdej] (count: 1, first: 2025-03-02T10:00:01+00:00, last: 2025-03-02T10:00:01+00:00)

## Evidence by Source
- `/home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/redacted_input.log` (evidence: 2 of 2, first: 2025-03-02T10:00:00+00:00)

## Suspected Components
- api (errors: 1)
- worker (errors: 1)
