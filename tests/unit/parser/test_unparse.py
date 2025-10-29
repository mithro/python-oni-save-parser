"""Tests for binary writing primitives."""

import struct

from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter


def test_write_uint32():
    """Should write unsigned 32-bit integer."""
    writer = BinaryWriter()
    writer.write_uint32(0x12345678)
    assert writer.data == struct.pack("<I", 0x12345678)


def test_write_int32():
    """Should write signed 32-bit integer."""
    writer = BinaryWriter()
    writer.write_int32(-42)
    assert writer.data == struct.pack("<i", -42)


def test_write_byte():
    """Should write single byte."""
    writer = BinaryWriter()
    writer.write_byte(0x42)
    writer.write_byte(0xFF)
    assert writer.data == b"\x42\xFF"


def test_write_bytes():
    """Should write raw bytes."""
    writer = BinaryWriter()
    writer.write_bytes(b"HELLO")
    assert writer.data == b"HELLO"


def test_write_chars():
    """Should write ASCII string."""
    writer = BinaryWriter()
    writer.write_chars("KSAV")
    assert writer.data == b"KSAV"


def test_round_trip_uint32():
    """uint32 should round-trip correctly."""
    writer = BinaryWriter()
    writer.write_uint32(0x87654321)
    parser = BinaryParser(writer.data)
    assert parser.read_uint32() == 0x87654321


def test_round_trip_int32():
    """int32 should round-trip correctly."""
    writer = BinaryWriter()
    writer.write_int32(-9999)
    parser = BinaryParser(writer.data)
    assert parser.read_int32() == -9999


def test_write_klei_string():
    """Should write length-prefixed UTF-8 string."""
    writer = BinaryWriter()
    writer.write_klei_string("Hello")
    expected = struct.pack("<i", 5) + b"Hello"
    assert writer.data == expected


def test_write_klei_string_empty():
    """Should handle empty string."""
    writer = BinaryWriter()
    writer.write_klei_string("")
    assert writer.data == struct.pack("<i", 0)


def test_write_klei_string_unicode():
    """Should handle unicode."""
    writer = BinaryWriter()
    text = "Hello 世界"
    writer.write_klei_string(text)
    encoded = text.encode("utf-8")
    expected = struct.pack("<i", len(encoded)) + encoded
    assert writer.data == expected


def test_write_additional_types():
    """Should write all primitive types."""
    writer = BinaryWriter()
    writer.write_uint16(0x1234)
    writer.write_int16(-1000)
    writer.write_uint64(0x123456789ABCDEF0)
    writer.write_int64(-9876543210)
    writer.write_single(3.14159)
    writer.write_double(3.141592653589793)
    writer.write_boolean(True)
    writer.write_boolean(False)

    parser = BinaryParser(writer.data)
    assert parser.read_uint16() == 0x1234
    assert parser.read_int16() == -1000
    assert parser.read_uint64() == 0x123456789ABCDEF0
    assert parser.read_int64() == -9876543210
    assert abs(parser.read_single() - 3.14159) < 0.00001
    assert abs(parser.read_double() - 3.141592653589793) < 0.0000000000001
    assert parser.read_boolean() is True
    assert parser.read_boolean() is False


def test_round_trip_klei_string():
    """KleiString should round-trip correctly."""
    writer = BinaryWriter()
    writer.write_klei_string("Test 测试")
    parser = BinaryParser(writer.data)
    assert parser.read_klei_string() == "Test 测试"


def test_write_klei_string_null():
    """Should write null marker for None."""
    writer = BinaryWriter()
    writer.write_klei_string(None)
    assert writer.data == struct.pack("<i", -1)


def test_round_trip_klei_string_null():
    """None should round-trip correctly."""
    writer = BinaryWriter()
    writer.write_klei_string(None)
    parser = BinaryParser(writer.data)
    assert parser.read_klei_string() is None
