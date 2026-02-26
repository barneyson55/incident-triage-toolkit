# Incident Timeline

T0: `2025-03-01T10:00:00+00:00`

## Events

| Time (UTC) | Level | Component | Message |
| --- | --- | --- | --- |
| 2025-03-01T10:00:00+00:00 | INFO | api | start cid=abc-1 |
| 2025-03-01T10:00:02+00:00 | ERROR | db | query failed cid=q-9 |
| 2025-03-01T10:00:03+00:00 | WARN | worker | retry in 30s |
| 2025-03-01T10:00:04+00:00 | ERROR | api | request 500 for user 42 |

## Notable Errors
- query failed cid=<id> (count: 1, first: 2025-03-01T10:00:02+00:00, last: 2025-03-01T10:00:02+00:00)
- request # for user # (count: 1, first: 2025-03-01T10:00:04+00:00, last: 2025-03-01T10:00:04+00:00)

## Suspected Components
- db (errors: 1)
- api (errors: 1)
