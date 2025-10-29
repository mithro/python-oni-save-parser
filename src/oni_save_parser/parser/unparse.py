"""Binary writing primitives for writing ONI save files."""

import struct


class BinaryWriter:
    """Low-level binary writer."""

    def __init__(self) -> None:
        """Initialize writer with empty buffer."""
        self._buffer: list[bytes] = []

    @property
    def data(self) -> bytes:
        """Get accumulated binary data."""
        return b"".join(self._buffer)

    def write_uint32(self, value: int) -> None:
        """Write unsigned 32-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<I", value))

    def write_int32(self, value: int) -> None:
        """Write signed 32-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<i", value))

    def write_byte(self, value: int) -> None:
        """Write single unsigned byte."""
        self._buffer.append(struct.pack("B", value))

    def write_bytes(self, value: bytes) -> None:
        """Write raw bytes."""
        self._buffer.append(value)

    def write_chars(self, value: str) -> None:
        """Write ASCII string (no length prefix)."""
        self._buffer.append(value.encode("ascii"))
