from __future__ import annotations

from .evidence import build_signature_evidence, component_counts, error_events, order_events, representative_correlation_ids
from .models import LogEvent


def _format_component_counts(items: list[tuple[str, int]]) -> str:
    if not items:
        return "none"
    return ", ".join(f"{component} ({count})" for component, count in items)


def _format_correlation_ids(correlation_ids: list[str]) -> str:
    if not correlation_ids:
        return "none"
    return ", ".join(f"`{correlation_id}`" for correlation_id in correlation_ids)


def _format_signature_list(signatures) -> str:
    if not signatures:
        return "none"
    return ", ".join(f"`{item.signature}` ({item.count})" for item in signatures)


def _incident_window(ordered: list[LogEvent]) -> str:
    if not ordered:
        return "`n/a`"
    return f"`{ordered[0].timestamp.isoformat()}` → `{ordered[-1].timestamp.isoformat()}`"


def build_runbook(events: list[LogEvent], title: str) -> str:
    ordered = order_events(events)
    evidence_events = error_events(ordered)
    signatures = build_signature_evidence(ordered, limit=3)
    top_components = component_counts(ordered, limit=3)
    correlation_ids = representative_correlation_ids(ordered, limit=3)

    first_observed = ordered[0].timestamp.isoformat() if ordered else "n/a"
    last_observed = ordered[-1].timestamp.isoformat() if ordered else "n/a"

    lines: list[str] = [
        f"# {title}",
        "",
        "## Symptoms",
        f"- Incident window: {_incident_window(ordered)}",
        f"- First observed: `{first_observed}`",
        f"- Last observed: `{last_observed}`",
        f"- Evidence events: {len(evidence_events)} of {len(ordered)} total",
        f"- Top error signatures: {_format_signature_list(signatures)}",
        f"- Suspected components: {_format_component_counts(top_components)}",
        f"- Representative correlation IDs: {_format_correlation_ids(correlation_ids)}",
    ]

    if not ordered:
        lines.append("- No parsed events matched the selected inputs or filters.")
    elif not evidence_events:
        lines.append("- Parsed events were present, but no error-like evidence was detected.")

    lines.extend(["", "## Evidence", "", "### Top Error Signatures"])
    if not signatures:
        lines.append("- None detected in parsed input.")
    else:
        for item in signatures:
            components = ", ".join(item.components) if item.components else "unknown"
            lines.append(
                "- {} (count: {}, first: {}, last: {}, components: {})".format(
                    item.signature,
                    item.count,
                    item.first_seen.isoformat(),
                    item.last_seen.isoformat(),
                    components,
                )
            )

    lines.extend(["", "### Example Failures"])
    if not signatures:
        lines.append("- No representative failures available.")
    else:
        for item in signatures:
            event = item.representative
            lines.append(
                "- `{}` `{}` `{}` — {}".format(
                    event.timestamp.isoformat(),
                    event.level,
                    event.component,
                    event.message.replace("\n", " "),
                )
            )

    lines.extend(["", "## Checks"])
    if top_components:
        lines.append(
            f"- Prioritize health and dependency checks for: {', '.join(component for component, _ in top_components)}."
        )
    else:
        lines.append("- Validate that the selected logs and filters cover the suspected incident window.")

    if correlation_ids:
        lines.append(f"- Trace these IDs through adjacent logs and traces: {', '.join(correlation_ids)}.")
    else:
        lines.append("- Search surrounding logs for a stable correlation ID or request key to anchor the incident.")

    if signatures:
        lines.append(
            f"- Compare the first and last evidence timestamps against deployments or config changes during {_incident_window(ordered)}."
        )
    else:
        lines.append("- If this empty evidence view is unexpected, widen filters or inspect parse diagnostics for dropped lines.")

    lines.extend(["", "## Workaround"])
    if top_components:
        lines.append(
            f"- Reduce traffic to, disable risky flows in, or otherwise contain the implicated components: {', '.join(component for component, _ in top_components)}."
        )
    else:
        lines.append("- Reduce customer impact with the safest reversible mitigation available while collecting better evidence.")
    lines.append("- Roll back, restart, or fail over the affected service only if that action is consistent with the evidence above.")

    lines.extend(["", "## Fix/Escalation"])
    if signatures:
        lines.append(
            f"- Escalate with the incident window, top signatures, and representative failures captured above: {_format_signature_list(signatures)}."
        )
    else:
        lines.append("- Escalate with the empty-evidence runbook plus raw input context if no stronger signal is available.")
    lines.append("- Attach the incident timeline and any supporting logs, dashboards, or deployment links needed to reproduce the failure.")

    lines.extend(["", "## Verification"])
    if signatures:
        lines.append(
            f"- Confirm the top signatures stop recurring after mitigation: {_format_signature_list(signatures)}."
        )
    else:
        lines.append("- Confirm the suspected customer impact is gone and that no new error evidence appears in refreshed logs.")
    lines.append("- Re-run the critical user flows that touch the implicated components and verify healthy responses.")

    lines.extend(
        [
            "",
            "## Notes",
            "- Add incident-specific decisions, links, owners, and next actions here.",
        ]
    )

    return "\n".join(lines) + "\n"
