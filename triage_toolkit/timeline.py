from __future__ import annotations

from .evidence import build_signature_evidence, build_source_evidence, component_counts, is_error, order_events, render_error_signature
from .models import LogEvent
from .redaction import redact_text


def _escape_markdown(text: str) -> str:
    return text.replace("|", "\\|")


def _format_event_source(event: LogEvent) -> str:
    if event.source_path is None or event.line_number is None:
        return "n/a"
    return f"{event.source_path}:{event.line_number}"


def _format_source_evidence(item, *, total_evidence_events: int) -> str:
    return "- `{}` (evidence: {} of {}, first: {})".format(
        item.source,
        item.count,
        total_evidence_events,
        item.first_seen.isoformat(),
    )


def build_timeline(events: list[LogEvent], *, redact: bool = False) -> str:
    if not events:
        return """# Incident Timeline\n\nT0: `n/a`\n\n## Events\n\n_No events parsed._\n\n## Notable Errors\n\n- None detected in parsed input.\n\n## Evidence by Source\n\n- No source concentration inferred.\n\n## Suspected Components\n\n- No components inferred.\n"""

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
        message = event.message.replace("\n", " ")
        if redact:
            message = redact_text(message)
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                event.timestamp.isoformat(),
                _escape_markdown(_format_event_source(event)),
                event.level,
                event.component,
                _escape_markdown(message),
            )
        )

    errors = [event for event in ordered if is_error(event)]
    lines.extend(["", "## Notable Errors"])
    if not errors:
        lines.append("- None detected in parsed input.")
    else:
        for evidence in build_signature_evidence(ordered):
            signature = evidence.signature
            if redact:
                signature = render_error_signature(evidence.representative.message, redact=True)
            lines.append(
                "- {} (count: {}, first: {}, last: {})".format(
                    signature,
                    evidence.count,
                    evidence.first_seen.isoformat(),
                    evidence.last_seen.isoformat(),
                )
            )

    lines.extend(["", "## Evidence by Source"])
    if not errors:
        lines.append("- No source concentration inferred.")
    else:
        for item in build_source_evidence(ordered):
            lines.append(_format_source_evidence(item, total_evidence_events=len(errors)))

    lines.extend(["", "## Suspected Components"])
    if not errors:
        lines.append("- No components inferred.")
    else:
        for component, count in component_counts(ordered):
            lines.append(f"- {component} (errors: {count})")

    return "\n".join(lines) + "\n"
