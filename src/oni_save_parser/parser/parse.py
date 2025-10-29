"""Binary parsing primitives for reading ONI save files."""

import struct

from .errors import CorruptionError


class BinaryParser:
    """Low-level binary reader with offset tracking."""

    def __init__(self, data: bytes):
        """Initialize parser with byte data.

        Args:
            data: Raw binary data to parse
        """
        self.data = data
        self.offset = 0

    def _read_struct(self, fmt: str, size: int) -> tuple[int, ...]:
        """Read structured data and advance offset.

        Args:
            fmt: struct format string
            size: number of bytes to read

        Returns:
            Tuple of unpacked values

        Raises:
            CorruptionError: If trying to read past end of data
        """
        if self.offset + size > len(self.data):
            raise CorruptionError(
                f"Unexpected end of data (need {size} bytes, have {len(self.data) - self.offset})",
                offset=self.offset,
            )
        values = struct.unpack_from(fmt, self.data, self.offset)
        self.offset += size
        return values

    def read_uint32(self) -> int:
        """Read unsigned 32-bit integer (little-endian)."""
        return self._read_struct("<I", 4)[0]

    def read_int32(self) -> int:
        """Read signed 32-bit integer (little-endian)."""
        return self._read_struct("<i", 4)[0]

    def read_uint16(self) -> int:
        """Read unsigned 16-bit integer (little-endian)."""
        return self._read_struct("<H", 2)[0]

    def read_int16(self) -> int:
        """Read signed 16-bit integer (little-endian)."""
        return self._read_struct("<h", 2)[0]

    def read_uint64(self) -> int:
        """Read unsigned 64-bit integer (little-endian)."""
        return self._read_struct("<Q", 8)[0]

    def read_int64(self) -> int:
        """Read signed 64-bit integer (little-endian)."""
        return self._read_struct("<q", 8)[0]

    def read_single(self) -> float:
        """Read 32-bit floating point (little-endian)."""
        return self._read_struct("<f", 4)[0]

    def read_double(self) -> float:
        """Read 64-bit floating point (little-endian)."""
        return self._read_struct("<d", 8)[0]

    def read_byte(self) -> int:
        """Read single unsigned byte."""
        return self._read_struct("B", 1)[0]

    def read_bytes(self, count: int) -> bytes:
        """Read raw bytes.

        Args:
            count: Number of bytes to read

        Returns:
            Raw bytes

        Raises:
            CorruptionError: If trying to read past end
        """
        if self.offset + count > len(self.data):
            raise CorruptionError(
                f"Unexpected end of data (need {count} bytes, have {len(self.data) - self.offset})",
                offset=self.offset,
            )
        value = self.data[self.offset : self.offset + count]
        self.offset += count
        return value

    def read_chars(self, count: int) -> str:
        """Read ASCII string of specific length.

        Args:
            count: Number of characters to read

        Returns:
            ASCII string
        """
        return self.read_bytes(count).decode("ascii")

    def read_boolean(self) -> bool:
        """Read boolean as single byte."""
        return self.read_byte() != 0

    def read_klei_string(self) -> str | None:
        """Read length-prefixed UTF-8 string (ONI format).

        Format: [int32 length][UTF-8 bytes]
        Special: length of -1 indicates null string

        Returns:
            Decoded UTF-8 string, or None if null marker (-1)

        Raises:
            CorruptionError: If length is invalid (< -1)
        """
        length = self.read_int32()
        if length == -1:
            return None
        if length == 0:
            return ""
        if length < 0:
            raise CorruptionError(
                f"Invalid string length {length} (must be >= -1)",
                offset=self.offset - 4,
            )
        return self.read_bytes(length).decode("utf-8")
