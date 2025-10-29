"""Save file header data structures and parsing."""

import json
from dataclasses import dataclass
from typing import Any

from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter


@dataclass
class SaveGameInfo:
    """Game information from save header.

    .NET Class: SaveGame+GameInfo
    Parser: SaveGame.GetGameInfo(byte[] bytes)
    """

    number_of_cycles: int
    number_of_duplicants: int
    base_name: str
    is_auto_save: bool
    original_save_name: str
    save_major_version: int
    save_minor_version: int
    cluster_id: str
    sandbox_enabled: bool
    colony_guid: str
    dlc_id: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "numberOfCycles": self.number_of_cycles,
            "numberOfDuplicants": self.number_of_duplicants,
            "baseName": self.base_name,
            "isAutoSave": self.is_auto_save,
            "originalSaveName": self.original_save_name,
            "saveMajorVersion": self.save_major_version,
            "saveMinorVersion": self.save_minor_version,
            "clusterId": self.cluster_id,
            "sandboxEnabled": self.sandbox_enabled,
            "colonyGuid": self.colony_guid,
            "dlcId": self.dlc_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SaveGameInfo":
        """Create from dictionary (from JSON)."""
        return cls(
            number_of_cycles=data["numberOfCycles"],
            number_of_duplicants=data["numberOfDuplicants"],
            base_name=data["baseName"],
            is_auto_save=data["isAutoSave"],
            original_save_name=data["originalSaveName"],
            save_major_version=data["saveMajorVersion"],
            save_minor_version=data["saveMinorVersion"],
            cluster_id=data["clusterId"],
            sandbox_enabled=data["sandboxEnabled"],
            colony_guid=data["colonyGuid"],
            dlc_id=data["dlcId"],
        )


@dataclass
class SaveGameHeader:
    """Save file header structure."""

    build_version: int
    header_version: int
    is_compressed: bool
    game_info: SaveGameInfo


def parse_header(parser: BinaryParser) -> SaveGameHeader:
    """Parse save file header.

    Args:
        parser: Binary parser positioned at header start

    Returns:
        Parsed save game header

    Raises:
        CorruptionError: If header data is invalid
    """
    build_version = parser.read_uint32()
    header_size = parser.read_uint32()
    header_version = parser.read_uint32()

    # Compression flag added in header version 1
    is_compressed = False
    if header_version >= 1:
        is_compressed = bool(parser.read_uint32())

    # Read game info JSON
    info_bytes = parser.read_bytes(header_size)
    try:
        info_str = info_bytes.decode("utf-8")
        game_info_dict = json.loads(info_str)
        game_info = SaveGameInfo.from_dict(game_info_dict)
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as e:
        raise CorruptionError(f"Failed to parse game info JSON: {e}", offset=parser.offset)

    return SaveGameHeader(
        build_version=build_version,
        header_version=header_version,
        is_compressed=is_compressed,
        game_info=game_info,
    )


def unparse_header(writer: BinaryWriter, header: SaveGameHeader) -> None:
    """Write save file header.

    Args:
        writer: Binary writer to append to
        header: Save game header to write
    """
    # Serialize game info to JSON
    game_info_dict = header.game_info.to_dict()
    info_str = json.dumps(game_info_dict)
    info_bytes = info_str.encode("utf-8")

    # Write header fields
    writer.write_uint32(header.build_version)
    writer.write_uint32(len(info_bytes))  # header size
    writer.write_uint32(header.header_version)

    # Compression flag (only for header version >= 1)
    if header.header_version >= 1:
        writer.write_uint32(1 if header.is_compressed else 0)

    # Write game info JSON
    writer.write_bytes(info_bytes)
