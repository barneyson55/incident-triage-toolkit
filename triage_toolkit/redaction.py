from __future__ import annotations

import hashlib
import re

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_IPV4_RE = re.compile(r"(?<![0-9A-Fa-f:.])(?:\d{1,3}\.){3}\d{1,3}(?![0-9A-Fa-f:.])")
_IPV6_RE = re.compile(r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}(?![0-9A-Fa-f:])")
_UUID_RE = re.compile(
    r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\b"
)
_CORRELATION_ID_RE = re.compile(
    r"(?P<key>\b(?:correlation[_-]?id|cid|trace[_-]?id|request[_-]?id)\b)\s*=\s*"
    r"(?P<value>[A-Za-z0-9][A-Za-z0-9._:-]{1,})",
    re.IGNORECASE,
)
_JWT_RE = re.compile(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_LONG_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_=-]{20,}\b")
_DIGIT_TRANSLATION = str.maketrans("0123456789", "abcdefghij")


def _stable_suffix(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12].translate(_DIGIT_TRANSLATION)


def _placeholder(kind: str, value: str) -> str:
    return f"[redacted-{kind}:{_stable_suffix(value)}]"


def redact_identifier(value: str) -> str:
    return _placeholder("id", value)


def _redact_secret_like_token(match: re.Match[str]) -> str:
    token = match.group(0)
    if not any(char.isalpha() for char in token):
        return token
    if not any(char.isdigit() for char in token):
        return token
    return _placeholder("secret", token)


def redact_text(text: str) -> str:
    redacted = _EMAIL_RE.sub(lambda match: _placeholder("email", match.group(0)), text)
    redacted = _CORRELATION_ID_RE.sub(
        lambda match: f"{match.group('key')}={redact_identifier(match.group('value'))}",
        redacted,
    )
    redacted = _UUID_RE.sub(lambda match: redact_identifier(match.group(0)), redacted)
    redacted = _IPV4_RE.sub(lambda match: _placeholder("ip", match.group(0)), redacted)
    redacted = _IPV6_RE.sub(lambda match: _placeholder("ip", match.group(0)), redacted)
    redacted = _JWT_RE.sub(lambda match: _placeholder("secret", match.group(0)), redacted)
    redacted = _LONG_TOKEN_RE.sub(_redact_secret_like_token, redacted)
    return redacted
