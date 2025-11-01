"""Tests for binary parsing primitives."""

import struct

import pytest

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser


def test_read_uint32() -> None:
    """Should read unsigned 32-bit integer (little-endian)."""
    data = struct.pack("<I", 0x12345678)
    parser = BinaryParser(data)
    assert parser.read_uint32() == 0x12345678
    assert parser.offset == 4


def test_read_int32() -> None:
    """Should read signed 32-bit integer (little-endian)."""
    data = struct.pack("<i", -42)
    parser = BinaryParser(data)
    assert parser.read_int32() == -42
    assert parser.offset == 4


def test_read_byte() -> None:
    """Should read single unsigned byte."""
    data = b"\x42\xff"
    parser = BinaryParser(data)
    assert parser.read_byte() == 0x42
    assert parser.read_byte() == 0xFF
    assert parser.offset == 2


def test_read_bytes() -> None:
    """Should read multiple bytes."""
    data = b"HELLO WORLD"
    parser = BinaryParser(data)
    assert parser.read_bytes(5) == b"HELLO"
    assert parser.offset == 5


def test_read_chars() -> None:
    """Should read ASCII string of specific length."""
    data = b"KSAV\x00\x00"
    parser = BinaryParser(data)
    assert parser.read_chars(4) == "KSAV"
    assert parser.offset == 4


def test_read_beyond_end_raises() -> None:
    """Should raise CorruptionError when reading past end."""
    data = b"\x01\x02"
    parser = BinaryParser(data)
    with pytest.raises(CorruptionError, match="Unexpected end"):
        parser.read_uint32()


def test_offset_tracking() -> None:
    """Should track offset correctly across reads."""
    data = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    parser = BinaryParser(data)
    assert parser.offset == 0
    parser.read_byte()
    assert parser.offset == 1
    parser.read_uint32()
    assert parser.offset == 5


def test_read_klei_string() -> None:
    """Should read length-prefixed UTF-8 string."""
    # String "Hello" = 5 bytes
    data = struct.pack("<i", 5) + b"Hello"
    parser = BinaryParser(data)
    assert parser.read_klei_string() == "Hello"
    assert parser.offset == 9  # 4 (length) + 5 (data)


def test_read_klei_string_empty() -> None:
    """Should handle empty string."""
    data = struct.pack("<i", 0)
    parser = BinaryParser(data)
    assert parser.read_klei_string() == ""
    assert parser.offset == 4


def test_read_klei_string_unicode() -> None:
    """Should handle unicode characters."""
    text = "Hello 世界"
    encoded = text.encode("utf-8")
    data = struct.pack("<i", len(encoded)) + encoded
    parser = BinaryParser(data)
    assert parser.read_klei_string() == text


def test_read_klei_string_null() -> None:
    """Should return None for null marker (-1)."""
    data = struct.pack("<i", -1)
    parser = BinaryParser(data)
    assert parser.read_klei_string() is None
    assert parser.offset == 4


def test_read_klei_string_invalid_negative() -> None:
    """Should raise CorruptionError for invalid negative lengths."""
    data = struct.pack("<i", -2)
    parser = BinaryParser(data)
    with pytest.raises(CorruptionError, match="Invalid string length -2"):
        parser.read_klei_string()


def test_read_klei_string_truncated() -> None:
    """Should raise CorruptionError when string data is truncated."""
    # Length says 10 bytes but only 5 are available
    data = struct.pack("<i", 10) + b"Hello"
    parser = BinaryParser(data)
    with pytest.raises(CorruptionError, match="Unexpected end"):
        parser.read_klei_string()


def test_read_uint16() -> None:
    """Should read unsigned 16-bit integer."""
    data = struct.pack("<H", 0x1234)
    parser = BinaryParser(data)
    assert parser.read_uint16() == 0x1234


def test_read_int16() -> None:
    """Should read signed 16-bit integer."""
    data = struct.pack("<h", -1000)
    parser = BinaryParser(data)
    assert parser.read_int16() == -1000


def test_read_uint64() -> None:
    """Should read unsigned 64-bit integer."""
    data = struct.pack("<Q", 0x123456789ABCDEF0)
    parser = BinaryParser(data)
    assert parser.read_uint64() == 0x123456789ABCDEF0


def test_read_int64() -> None:
    """Should read signed 64-bit integer."""
    data = struct.pack("<q", -9876543210)
    parser = BinaryParser(data)
    assert parser.read_int64() == -9876543210


def test_read_single() -> None:
    """Should read 32-bit float."""
    data = struct.pack("<f", 3.14159)
    parser = BinaryParser(data)
    result = parser.read_single()
    assert abs(result - 3.14159) < 0.00001


def test_read_double() -> None:
    """Should read 64-bit double."""
    data = struct.pack("<d", 3.141592653589793)
    parser = BinaryParser(data)
    result = parser.read_double()
    assert abs(result - 3.141592653589793) < 0.0000000000001


def test_read_boolean() -> None:
    """Should read boolean as byte."""
    data = b"\x01\x00"
    parser = BinaryParser(data)
    assert parser.read_boolean() is True
    assert parser.read_boolean() is False
