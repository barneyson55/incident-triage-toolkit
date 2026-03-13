from __future__ import annotations

import re


_BACKTICK_RUN_RE = re.compile(r"`+")


def markdown_safe_text(text: str, *, escape_backticks: bool = False) -> str:
    sanitized = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    if escape_backticks:
        sanitized = sanitized.replace("`", "\\`")
    return sanitized


def markdown_code_span(text: str) -> str:
    sanitized = markdown_safe_text(text)
    longest_backtick_run = max((len(match.group(0)) for match in _BACKTICK_RUN_RE.finditer(sanitized)), default=0)
    fence = "`" * (longest_backtick_run + 1)
    if sanitized.startswith(("`", " ")) or sanitized.endswith(("`", " ")):
        sanitized = f" {sanitized} "
    return f"{fence}{sanitized}{fence}"
