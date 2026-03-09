# Incident Timeline

T0: `2025-03-01T10:00:00+00:00`

## Events

| Time (UTC) | Source | Level | Component | Message |
| --- | --- | --- | --- | --- |
| 2025-03-01T10:00:00+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/mixed_input.log:1 | INFO | api | start cid=abc-1 |
| 2025-03-01T10:00:02+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/mixed_input.log:3 | ERROR | db | query failed cid=q-9 |
| 2025-03-01T10:00:03+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/mixed_input.log:4 | WARN | worker | retry in 30s |
| 2025-03-01T10:00:04+00:00 | /home/node/.openclaw/workspace/projects/core/incident-triage-toolkit/tests/fixtures/golden/mixed_input.log:5 | ERROR | api | request 500 for user 42 |

## Notable Errors
- query failed cid=<id> (count: 1, first: 2025-03-01T10:00:02+00:00, last: 2025-03-01T10:00:02+00:00)
- request # for user # (count: 1, first: 2025-03-01T10:00:04+00:00, last: 2025-03-01T10:00:04+00:00)

## Suspected Components
- db (errors: 1)
- api (errors: 1)
