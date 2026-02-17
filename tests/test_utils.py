from triage_toolkit.utils import parse_timestamp


def test_parse_timestamp_empty_value_returns_none():
    assert parse_timestamp("") is None
    assert parse_timestamp("   ") is None


def test_parse_timestamp_naive_value_assumes_utc():
    parsed = parse_timestamp("2025-01-01 03:04:05")

    assert parsed is not None
    assert parsed.isoformat() == "2025-01-01T03:04:05+00:00"


def test_parse_timestamp_offset_value_normalizes_to_utc():
    parsed = parse_timestamp("2025-01-01T05:04:05+02:00")

    assert parsed is not None
    assert parsed.isoformat() == "2025-01-01T03:04:05+00:00"


def test_parse_timestamp_invalid_z_value_returns_none():
    assert parse_timestamp("2025-99-99T03:04:05Z") is None


def test_parse_timestamp_invalid_value_returns_none():
    assert parse_timestamp("not-a-timestamp") is None
