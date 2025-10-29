"""Parser exception types."""


class ParseError(Exception):
    """Base exception for all parsing errors."""

    pass


class VersionMismatchError(ParseError):
    """Raised when save file version is incompatible."""

    def __init__(
        self,
        expected_major: int,
        expected_minor: int,
        actual_major: int,
        actual_minor: int,
    ):
        self.expected_major = expected_major
        self.expected_minor = expected_minor
        self.actual_major = actual_major
        self.actual_minor = actual_minor
        super().__init__(
            f"Save version {actual_major}.{actual_minor} is incompatible. "
            f"Expected {expected_major}.{expected_minor}"
        )


class CorruptionError(ParseError):
    """Raised when save file data is corrupted."""

    def __init__(self, message: str, offset: int | None = None):
        self.offset = offset
        if offset is not None:
            message = f"{message} at offset 0x{offset:x}"
        super().__init__(message)
