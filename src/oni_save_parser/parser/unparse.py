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

    @property
    def position(self) -> int:
        """Get current write position (total bytes written)."""
        return len(self.data)

    def write_uint32(self, value: int) -> None:
        """Write unsigned 32-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<I", value))

    def write_int32(self, value: int) -> None:
        """Write signed 32-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<i", value))

    def write_byte(self, value: int) -> None:
        """Write single unsigned byte."""
        self._buffer.append(struct.pack("B", value))

    def write_sbyte(self, value: int) -> None:
        """Write single signed byte."""
        self._buffer.append(struct.pack("b", value))

    def write_bytes(self, value: bytes) -> None:
        """Write raw bytes."""
        self._buffer.append(value)

    def write_chars(self, value: str) -> None:
        """Write ASCII string (no length prefix)."""
        self._buffer.append(value.encode("ascii"))

    def write_klei_string(self, value: str | None) -> None:
        """Write length-prefixed UTF-8 string (ONI format).

        Format: [int32 length][UTF-8 bytes]
        Special: None writes -1 marker for null string
        """
        if value is None:
            self.write_int32(-1)
            return

        encoded = value.encode("utf-8")
        self.write_int32(len(encoded))
        if encoded:
            self.write_bytes(encoded)

    def write_uint16(self, value: int) -> None:
        """Write unsigned 16-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<H", value))

    def write_int16(self, value: int) -> None:
        """Write signed 16-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<h", value))

    def write_uint64(self, value: int) -> None:
        """Write unsigned 64-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<Q", value))

    def write_int64(self, value: int) -> None:
        """Write signed 64-bit integer (little-endian)."""
        self._buffer.append(struct.pack("<q", value))

    def write_single(self, value: float) -> None:
        """Write 32-bit floating point (little-endian)."""
        self._buffer.append(struct.pack("<f", value))

    def write_double(self, value: float) -> None:
        """Write 64-bit floating point (little-endian)."""
        self._buffer.append(struct.pack("<d", value))

    def write_boolean(self, value: bool) -> None:
        """Write boolean as single byte."""
        self.write_byte(1 if value else 0)

    def write_with_length(self, data: bytes) -> None:
        """Write data with int32 length prefix.

        Format: [int32 length][data bytes]
        This is used for object serialization with data-length tracking.
        """
        self.write_int32(len(data))
        if data:
            self.write_bytes(data)
