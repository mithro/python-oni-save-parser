"""Utility functions for ONI save parsing."""

import ctypes


def get_sdbm32_lower_hash(s: str) -> int:
    """Hash a string using SDBM algorithm (ONI's HashedString).

    This is the algorithm ONI uses for HashedString, whose values
    appear throughout the save file for element names, traits, etc.

    Args:
        s: String to hash (will be lowercased)

    Returns:
        Signed 32-bit integer hash
    """
    if not s:
        return 0

    s = s.lower()
    num = 0

    for char in s:
        # SDBM algorithm: hash = char + (hash << 6) + (hash << 16) - hash
        # Cast to int32 after each iteration to match TypeScript overflow behavior
        num = ord(char) + (num << 6) + (num << 16) - num
        num = ctypes.c_int32(num).value

    return num
