import re

from triage_toolkit.redaction import redact_identifier, redact_text


PLACEHOLDER_RE = r"\[redacted-(?P<kind>[a-z]+):(?P<suffix>[a-z]+)\]"


def _extract_placeholders(text: str, kind: str) -> list[str]:
    return re.findall(rf"\[redacted-{kind}:[a-z]+\]", text)


def test_redact_identifier_is_deterministic_and_letter_only():
    first = redact_identifier("550e8400-e29b-41d4-a716-446655440000")
    second = redact_identifier("550e8400-e29b-41d4-a716-446655440000")
    different = redact_identifier("550e8400-e29b-41d4-a716-446655440001")

    assert first == second
    assert first != different
    assert re.fullmatch(PLACEHOLDER_RE, first) is not None
    assert re.fullmatch(r"\[redacted-id:[a-z]{12}\]", first) is not None


def test_redact_text_reuses_email_and_ip_placeholders():
    email = "alice@example.com"
    ipv4 = "10.2.3.4"
    ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    redacted = redact_text(f"{email} {email} {ipv4} {ipv4} {ipv6} {ipv6}")

    email_placeholders = _extract_placeholders(redacted, "email")
    ip_placeholders = _extract_placeholders(redacted, "ip")

    assert email not in redacted
    assert ipv4 not in redacted
    assert ipv6 not in redacted
    assert email_placeholders == [email_placeholders[0], email_placeholders[0]]
    assert ip_placeholders == [ip_placeholders[0], ip_placeholders[0], ip_placeholders[2], ip_placeholders[2]]
    assert ip_placeholders[0] != ip_placeholders[2]


def test_redact_text_reuses_uuid_and_preserves_keyed_identifier_names_without_double_redaction():
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.c2lnbmF0dXJl"
    token = "AbCdEfGhIjKlMnOpQrSt123456"

    redacted = redact_text(f"uuid={uuid} cid={jwt} trace_id={uuid} request_id={token} cid={jwt}")

    uuid_placeholder = redact_identifier(uuid)
    jwt_placeholder = redact_identifier(jwt)
    token_placeholder = redact_identifier(token)

    assert redacted == (
        f"uuid={uuid_placeholder} cid={jwt_placeholder} trace_id={uuid_placeholder} "
        f"request_id={token_placeholder} cid={jwt_placeholder}"
    )
    assert "cid=" in redacted
    assert "trace_id=" in redacted
    assert "request_id=" in redacted
    assert "[redacted-secret:" not in redacted
    assert "[redacted-id:[redacted-" not in redacted


def test_redact_text_reuses_secret_placeholders_for_jwts_and_mixed_long_tokens():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.c2lnbmF0dXJl"
    secret = "AbCdEfGhIjKlMnOpQrSt123456"

    redacted = redact_text(f"jwt={jwt} jwt={jwt} token={secret} token={secret}")

    secret_placeholders = _extract_placeholders(redacted, "secret")

    assert jwt not in redacted
    assert secret not in redacted
    assert secret_placeholders == [secret_placeholders[0], secret_placeholders[0], secret_placeholders[2], secret_placeholders[2]]
    assert secret_placeholders[0] != secret_placeholders[2]


def test_redact_text_long_token_boundaries_skip_all_digits_and_all_alpha_but_redact_mixed_tokens():
    digits_only = "12345678901234567890"
    alpha_only = "abcdefghijklmnopqrstuvwx"
    mixed = "abc123def456ghi789jkl0"

    redacted = redact_text(f"tokens: {digits_only} {alpha_only} {mixed}")

    assert digits_only in redacted
    assert alpha_only in redacted
    assert mixed not in redacted
    assert len(_extract_placeholders(redacted, "secret")) == 1
