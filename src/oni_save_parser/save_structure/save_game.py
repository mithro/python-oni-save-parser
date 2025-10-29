"""Main save game data structure."""

import zlib
from dataclasses import dataclass
from typing import Any

from oni_save_parser.parser.errors import CorruptionError, VersionMismatchError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.game_objects import (
    GameObjectGroup,
    parse_game_objects,
    unparse_game_objects,
)
from oni_save_parser.save_structure.header import SaveGameHeader, parse_header, unparse_header
from oni_save_parser.save_structure.type_templates import (
    TypeTemplate,
    parse_by_template,
    parse_templates,
    unparse_by_template,
    unparse_templates,
    validate_dotnet_identifier_name,
)

SAVE_HEADER = "KSAV"


@dataclass
class SaveGame:
    """Complete ONI save game structure."""

    header: SaveGameHeader
    templates: list[TypeTemplate]
    world: dict[str, Any]  # Klei.SaveFileRoot template data
    settings: dict[str, Any]  # Game+Settings template data
    sim_data: bytes  # Simulation data (binary blob)
    version_major: int
    version_minor: int
    game_objects: list[GameObjectGroup]  # Game entities organized by prefab
    game_data: bytes  # Additional game state (format TBD)


def parse_save_game(
    data: bytes, verify_version: bool = True, allow_minor_mismatch: bool = False
) -> SaveGame:
    """Parse complete ONI save game.

    Args:
        data: Raw save file bytes
        verify_version: Whether to verify save version compatibility
        allow_minor_mismatch: If True, allow different minor versions (less safe)

    Returns:
        Parsed save game structure

    Raises:
        VersionMismatchError: If save version is incompatible
        CorruptionError: If save data is corrupted
    """
    parser = BinaryParser(data)

    # Parse header
    header = parse_header(parser)

    # Verify version if requested
    if verify_version:
        expected_major = 7  # Current ONI save version
        expected_minor = 35
        actual_major = header.game_info.save_major_version
        actual_minor = header.game_info.save_minor_version

        if actual_major != expected_major:
            raise VersionMismatchError(expected_major, expected_minor, actual_major, actual_minor)

        if not allow_minor_mismatch and actual_minor != expected_minor:
            raise VersionMismatchError(expected_major, expected_minor, actual_major, actual_minor)

    # Parse type templates
    templates = parse_templates(parser)

    # Parse body (potentially compressed)
    if header.is_compressed:
        # Read remaining data and decompress
        body_data = parser.data[parser.offset :]
        try:
            decompressed = zlib.decompress(body_data, wbits=15)
        except zlib.error as e:
            raise CorruptionError(f"Failed to decompress save body: {e}", offset=parser.offset)
        body_parser = BinaryParser(decompressed)
    else:
        body_parser = parser

    # Parse body structure
    (
        world,
        settings,
        sim_data,
        version_major,
        version_minor,
        game_objects,
        game_data,
    ) = _parse_save_body(body_parser, templates)

    return SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=sim_data,
        version_major=version_major,
        version_minor=version_minor,
        game_objects=game_objects,
        game_data=game_data,
    )


def _parse_save_body(
    parser: BinaryParser, templates: list[TypeTemplate]
) -> tuple[dict[str, Any], dict[str, Any], bytes, int, int, list[GameObjectGroup], bytes]:
    """Parse save game body.

    Returns:
        Tuple of (world, settings, sim_data, version_major, version_minor,
                  game_objects, game_data)
    """
    # Expect "world" marker
    world_marker = parser.read_klei_string()
    if world_marker != "world":
        raise CorruptionError(
            f'Expected "world" marker, got "{world_marker}"', offset=parser.offset
        )

    # Parse world (Klei.SaveFileRoot)
    world_type_name = parser.read_klei_string()
    if world_type_name is None:
        raise CorruptionError("Expected world type name, got null", offset=parser.offset)
    validate_dotnet_identifier_name(world_type_name)
    if world_type_name != "Klei.SaveFileRoot":
        raise CorruptionError(
            f'Expected world type "Klei.SaveFileRoot", got "{world_type_name}"',
            offset=parser.offset,
        )
    world = parse_by_template(parser, templates, world_type_name)

    # Parse settings (Game+Settings)
    settings_type_name = parser.read_klei_string()
    if settings_type_name is None:
        raise CorruptionError("Expected settings type name, got null", offset=parser.offset)
    validate_dotnet_identifier_name(settings_type_name)
    if settings_type_name != "Game+Settings":
        raise CorruptionError(
            f'Expected settings type "Game+Settings", got "{settings_type_name}"',
            offset=parser.offset,
        )
    settings = parse_by_template(parser, templates, settings_type_name)

    # SimData - length-prefixed binary blob
    sim_data_length = parser.read_int32()
    sim_data = parser.read_bytes(sim_data_length)

    # KSAV marker
    ksav_marker = parser.read_chars(len(SAVE_HEADER))
    if ksav_marker != SAVE_HEADER:
        raise CorruptionError(
            f'Expected "{SAVE_HEADER}" marker, got "{ksav_marker}"', offset=parser.offset
        )

    # Version
    version_major = parser.read_int32()
    version_minor = parser.read_int32()

    # Parse game objects
    game_objects = parse_game_objects(parser, templates)

    # Game data - remaining data
    # TODO: Implement game data parser (Phase 4.3)
    game_data = parser.data[parser.offset :]

    return (
        world,
        settings,
        sim_data,
        version_major,
        version_minor,
        game_objects,
        game_data,
    )


def unparse_save_game(save_game: SaveGame) -> bytes:
    """Write save game to binary format.

    Args:
        save_game: Save game structure to write

    Returns:
        Binary save file data
    """
    writer = BinaryWriter()

    # Write header
    unparse_header(writer, save_game.header)

    # Write templates
    unparse_templates(writer, save_game.templates)

    # Write body (potentially compress)
    body_writer = BinaryWriter()
    _unparse_save_body(body_writer, save_game)

    if save_game.header.is_compressed:
        # Compress body
        compressed = zlib.compress(body_writer.data, level=9, wbits=15)
        writer.write_bytes(compressed)
    else:
        writer.write_bytes(body_writer.data)

    return writer.data


def _unparse_save_body(writer: BinaryWriter, save_game: SaveGame) -> None:
    """Write save game body."""
    # World marker
    writer.write_klei_string("world")

    # World type and data
    writer.write_klei_string("Klei.SaveFileRoot")
    unparse_by_template(writer, save_game.templates, "Klei.SaveFileRoot", save_game.world)

    # Settings type and data
    writer.write_klei_string("Game+Settings")
    unparse_by_template(writer, save_game.templates, "Game+Settings", save_game.settings)

    # SimData
    writer.write_int32(len(save_game.sim_data))
    writer.write_bytes(save_game.sim_data)

    # KSAV marker
    writer.write_chars(SAVE_HEADER)

    # Version
    writer.write_int32(save_game.version_major)
    writer.write_int32(save_game.version_minor)

    # Game objects
    unparse_game_objects(writer, save_game.templates, save_game.game_objects)

    # Game data
    writer.write_bytes(save_game.game_data)
