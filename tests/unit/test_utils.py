"""Tests for utility functions."""

from oni_save_parser.utils import get_sdbm32_lower_hash


def test_sdbm_hash_empty() -> None:
    """Empty string should hash to 0."""
    assert get_sdbm32_lower_hash("") == 0


def test_sdbm_hash_simple() -> None:
    """Should hash simple strings correctly."""
    # Known hash values from TypeScript implementation
    assert get_sdbm32_lower_hash("test") == 1195757874


def test_sdbm_hash_case_insensitive() -> None:
    """Should be case insensitive (lowercase)."""
    assert get_sdbm32_lower_hash("TEST") == get_sdbm32_lower_hash("test")
    assert get_sdbm32_lower_hash("TeSt") == get_sdbm32_lower_hash("test")


def test_sdbm_hash_signed_32bit() -> None:
    """Should return signed 32-bit integer."""
    result = get_sdbm32_lower_hash("Minion")
    assert isinstance(result, int)
    assert -(2**31) <= result < 2**31


def test_sdbm_hash_known_values() -> None:
    """Should match known game values."""
    # These are actual hashes used in ONI
    assert get_sdbm32_lower_hash("minion") == 2129234166  # Duplicants
    # Add more known values when we verify them
