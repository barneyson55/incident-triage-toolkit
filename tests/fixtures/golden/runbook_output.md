# Incident: Golden

## Symptoms
- First observed: `2025-03-01T10:00:00+00:00`
- Error events: 2 of 4 total
- Suspected components: db, api

## Checks
- Review recent deployments or config changes for suspected components.
- Validate health endpoints and dependency connectivity.
- Inspect logs for correlation IDs tied to failures.

## Workaround
- Reduce traffic or disable the failing feature if possible.
- Roll back or restart the affected service to restore stability.

## Fix/Escalation
- Identify the root cause from error signatures and stack traces.
- Escalate to the owning team with a timeline and sample logs.

## Verification
- Confirm error rate returns to baseline.
- Re-run critical user flows and verify healthy responses.

## Notes
- Add incident-specific observations, links, and decisions here.
