import pytest

from triage_toolkit.utils import extract_correlation_id, parse_timestamp


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2025-01-01 03:04:05", "2025-01-01T03:04:05+00:00"),
        ("2025-01-01T03:04:05", "2025-01-01T03:04:05+00:00"),
        ("2025-01-01 03:04:05.123456", "2025-01-01T03:04:05.123456+00:00"),
        ("2025-01-01T03:04:05.123456", "2025-01-01T03:04:05.123456+00:00"),
    ],
)
def test_parse_timestamp_naive_shapes_assume_utc(value: str, expected: str):
    parsed = parse_timestamp(value)

    assert parsed is not None
    assert parsed.isoformat() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2025-01-01T05:04:05+02:00", "2025-01-01T03:04:05+00:00"),
        ("2025-01-01 05:04:05+02:00", "2025-01-01T03:04:05+00:00"),
        ("2025-01-01 05:04:05.123456+02:00", "2025-01-01T03:04:05.123456+00:00"),
    ],
)
def test_parse_timestamp_offset_aware_shapes_normalize_to_utc(value: str, expected: str):
    parsed = parse_timestamp(value)

    assert parsed is not None
    assert parsed.isoformat() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2025-01-01T03:04:05Z", "2025-01-01T03:04:05+00:00"),
        ("2025-01-01T03:04:05.123456Z", "2025-01-01T03:04:05.123456+00:00"),
    ],
)
def test_parse_timestamp_trailing_z_shapes_normalize_to_utc(value: str, expected: str):
    parsed = parse_timestamp(value)

    assert parsed is not None
    assert parsed.isoformat() == expected


def test_parse_timestamp_empty_value_returns_none():
    assert parse_timestamp("") is None
    assert parse_timestamp("   ") is None


@pytest.mark.parametrize(
    "value",
    [
        "not-a-timestamp",
        "2025-99-99T03:04:05Z",
        "2025-13-01 03:04:05",
        "2025-01-01T03:04:05+24:00",
        "2025-01-01T03:04:05+2:00",
        "2025-01-01T03:04:05Z+00:00",
    ],
)
def test_parse_timestamp_invalid_shapes_return_none(value: str):
    assert parse_timestamp(value) is None


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("request accepted cid=abc-123", "abc-123"),
        ("worker correlation_id=req-7 retrying", "req-7"),
        ("correlation_id=req-7 cid=abc-123", "req-7"),
    ],
)
def test_extract_correlation_id_supported_patterns(message: str, expected: str):
    assert extract_correlation_id(message) == expected


@pytest.mark.parametrize(
    "message",
    [
        "request accepted",
        "request accepted CID=abc-123",
        "request accepted cid= abc-123",
        "request accepted cid=",
        "request accepted correlation-id=req-7",
        "",
        None,
    ],
)
def test_extract_correlation_id_non_matches_return_none(message: str | None):
    assert extract_correlation_id(message) is None
