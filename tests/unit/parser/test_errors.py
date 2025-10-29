"""Tests for parser error types."""

import pytest
from oni_save_parser.parser.errors import (
    ParseError,
    VersionMismatchError,
    CorruptionError,
)


def test_parse_error_base():
    """ParseError should be base exception."""
    err = ParseError("test message")
    assert str(err) == "test message"
    assert isinstance(err, Exception)


def test_version_mismatch_error():
    """VersionMismatchError should include version info."""
    err = VersionMismatchError(7, 31, 7, 17)
    assert "7.31" in str(err)
    assert "7.17" in str(err)
    assert isinstance(err, ParseError)


def test_corruption_error():
    """CorruptionError should include context."""
    err = CorruptionError("Invalid header", offset=0x10)
    assert "Invalid header" in str(err)
    assert "0x10" in str(err) or "16" in str(err)
    assert isinstance(err, ParseError)
