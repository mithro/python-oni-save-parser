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
