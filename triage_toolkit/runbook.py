from __future__ import annotations

from collections import Counter

from .models import LogEvent
from .timeline import is_error


def build_runbook(events: list[LogEvent], title: str) -> str:
    ordered = sorted(events, key=lambda event: event.timestamp)
    t0 = ordered[0].timestamp if ordered else None
    errors = [event for event in ordered if is_error(event)]
    component_counts = Counter(event.component for event in errors)
    top_components = [component for component, _ in component_counts.most_common(3)]

    lines: list[str] = [f"# {title}", "", "## Symptoms"]
    if t0:
        lines.append(f"- First observed: `{t0.isoformat()}`")
    if errors:
        lines.append(f"- Error events: {len(errors)} of {len(events)} total")
    if top_components:
        lines.append(f"- Suspected components: {', '.join(top_components)}")
    if not events:
        lines.append("- No events parsed from input.")

    lines.extend(
        [
            "",
            "## Checks",
            "- Review recent deployments or config changes for suspected components.",
            "- Validate health endpoints and dependency connectivity.",
            "- Inspect logs for correlation IDs tied to failures.",
            "",
            "## Workaround",
            "- Reduce traffic or disable the failing feature if possible.",
            "- Roll back or restart the affected service to restore stability.",
            "",
            "## Fix/Escalation",
            "- Identify the root cause from error signatures and stack traces.",
            "- Escalate to the owning team with a timeline and sample logs.",
            "",
            "## Verification",
            "- Confirm error rate returns to baseline.",
            "- Re-run critical user flows and verify healthy responses.",
            "",
            "## Notes",
            "- Add incident-specific observations, links, and decisions here.",
        ]
    )

    return "\n".join(lines) + "\n"
