from __future__ import annotations

from collections import Counter, defaultdict
import re

from .models import LogEvent

_ERROR_LEVELS = {"ERROR", "CRITICAL", "FATAL"}
_DIGIT_RE = re.compile(r"\d+")
_CORR_RE = re.compile(r"(?:correlation_id|cid)=[A-Za-z0-9-]+", re.IGNORECASE)


def is_error(event: LogEvent) -> bool:
    if event.level.upper() in _ERROR_LEVELS:
        return True
    return "error" in event.message.lower()


def _normalize_message(message: str) -> str:
    text = message.lower().strip()
    text = _CORR_RE.sub("cid=<id>", text)
    text = _DIGIT_RE.sub("#", text)
    return text


def _escape_markdown(text: str) -> str:
    return text.replace("|", "\\|")


def build_timeline(events: list[LogEvent]) -> str:
    if not events:
        return """# Incident Timeline\n\nT0: `n/a`\n\n## Events\n\n_No events parsed._\n\n## Notable Errors\n\n- None detected in parsed input.\n\n## Suspected Components\n\n- No components inferred.\n"""

    ordered = sorted(events, key=lambda event: event.timestamp)
    t0 = ordered[0].timestamp

    lines: list[str] = [
        "# Incident Timeline",
        "",
        f"T0: `{t0.isoformat()}`",
        "",
        "## Events",
        "",
        "| Time (UTC) | Level | Component | Message |",
        "| --- | --- | --- | --- |",
    ]

    for event in ordered:
        lines.append(
            "| {} | {} | {} | {} |".format(
                event.timestamp.isoformat(),
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
        grouped: dict[str, list[LogEvent]] = defaultdict(list)
        for event in errors:
            grouped[_normalize_message(event.message)].append(event)
        for signature, items in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True):
            first_seen = min(items, key=lambda event: event.timestamp).timestamp
            last_seen = max(items, key=lambda event: event.timestamp).timestamp
            lines.append(
                f"- {signature} (count: {len(items)}, first: {first_seen.isoformat()}, last: {last_seen.isoformat()})"
            )

    lines.extend(["", "## Suspected Components"])
    if not errors:
        lines.append("- No components inferred.")
    else:
        counts = Counter(event.component for event in errors)
        for component, count in counts.most_common(5):
            lines.append(f"- {component} (errors: {count})")

    return "\n".join(lines) + "\n"
