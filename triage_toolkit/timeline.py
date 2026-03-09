from __future__ import annotations

from .evidence import build_signature_evidence, component_counts, is_error, order_events
from .models import LogEvent


def _escape_markdown(text: str) -> str:
    return text.replace("|", "\\|")


def _format_event_source(event: LogEvent) -> str:
    if event.source_path is None or event.line_number is None:
        return "n/a"
    return f"{event.source_path}:{event.line_number}"


def build_timeline(events: list[LogEvent]) -> str:
    if not events:
        return """# Incident Timeline\n\nT0: `n/a`\n\n## Events\n\n_No events parsed._\n\n## Notable Errors\n\n- None detected in parsed input.\n\n## Suspected Components\n\n- No components inferred.\n"""

    ordered = order_events(events)
    t0 = ordered[0].timestamp

    lines: list[str] = [
        "# Incident Timeline",
        "",
        f"T0: `{t0.isoformat()}`",
        "",
        "## Events",
        "",
        "| Time (UTC) | Source | Level | Component | Message |",
        "| --- | --- | --- | --- | --- |",
    ]

    for event in ordered:
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                event.timestamp.isoformat(),
                _escape_markdown(_format_event_source(event)),
                event.level,
                event.component,
                _escape_markdown(event.message.replace("\n", " ")),
            )
        )

    errors = [event for event in ordered if is_error(event)]
    lines.extend(["", "## Notable Errors"])
    if not errors:
        lines.append("- None detected in parsed input.")
    else:
        for evidence in build_signature_evidence(ordered):
            lines.append(
                "- {} (count: {}, first: {}, last: {})".format(
                    evidence.signature,
                    evidence.count,
                    evidence.first_seen.isoformat(),
                    evidence.last_seen.isoformat(),
                )
            )

    lines.extend(["", "## Suspected Components"])
    if not errors:
        lines.append("- No components inferred.")
    else:
        for component, count in component_counts(ordered):
            lines.append(f"- {component} (errors: {count})")

    return "\n".join(lines) + "\n"
