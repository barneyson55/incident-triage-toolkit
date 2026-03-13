from __future__ import annotations


def markdown_safe_text(text: str) -> str:
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", "\\|")
