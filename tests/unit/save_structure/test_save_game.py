"""Tests for save game parsing and unparsing."""

import zlib

import pytest

from oni_save_parser.parser.errors import CorruptionError, VersionMismatchError
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.save_game import (
    SaveGame,
    parse_save_game,
    unparse_save_game,
)
from oni_save_parser.save_structure.type_templates import (
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
    unparse_templates,
)


def create_test_header(
    compressed: bool = True,
    save_major: int = 7,
    save_minor: int = 35,
) -> SaveGameHeader:
    """Create a test save game header."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=5,
        base_name="TestBase",
        is_auto_save=False,
        original_save_name="TestBase Cycle 100",
        save_major_version=save_major,
        save_minor_version=save_minor,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="12345678-1234-1234-1234-123456789012",
        dlc_id="",
    )
    return SaveGameHeader(
        build_version=555555,
        header_version=1,
        is_compressed=compressed,
        game_info=game_info,
    )


def create_test_templates() -> list[TypeTemplate]:
    """Create minimal test type templates."""
    # Klei.SaveFileRoot template with minimal fields
    # Type codes: Int32=6, String=12
    world_template = TypeTemplate(
        name="Klei.SaveFileRoot",
        fields=[
            TypeTemplateMember(name="buildVersion", type=TypeInfo(info=6)),  # Int32
            TypeTemplateMember(name="worldID", type=TypeInfo(info=12)),  # String
        ],
        properties=[],
    )

    # Game+Settings template with minimal fields
    settings_template = TypeTemplate(
        name="Game+Settings",
        fields=[
            TypeTemplateMember(name="autoSaveCycleInterval", type=TypeInfo(info=6)),  # Int32
            TypeTemplateMember(name="difficulty", type=TypeInfo(info=6)),  # Int32
        ],
        properties=[],
    )

    return [world_template, settings_template]


def create_test_save_game(compressed: bool = True) -> SaveGame:
    """Create a minimal test save game structure."""
    header = create_test_header(compressed=compressed)
    templates = create_test_templates()

    world = {
        "buildVersion": 123456,
        "worldID": "TestWorld",
    }

    settings = {
        "autoSaveCycleInterval": 10,
        "difficulty": 1,
    }

    sim_data = b"\x01\x02\x03\x04\x05"

    return SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=sim_data,
        version_major=7,
        version_minor=35,
        game_objects=[],  # Empty game objects list
        game_data=b"",  # Empty game data
    )


def test_parse_save_game_compressed():
    """Should parse compressed save game."""
    save_game = create_test_save_game(compressed=True)
    data = unparse_save_game(save_game)

    parsed = parse_save_game(data)

    assert parsed.header.is_compressed is True
    assert parsed.header.game_info.save_major_version == 7
    assert parsed.header.game_info.save_minor_version == 35
    assert len(parsed.templates) == 2
    assert parsed.world["buildVersion"] == 123456
    assert parsed.world["worldID"] == "TestWorld"
    assert parsed.settings["autoSaveCycleInterval"] == 10
    assert parsed.sim_data == b"\x01\x02\x03\x04\x05"
    assert parsed.version_major == 7
    assert parsed.version_minor == 35


def test_parse_save_game_uncompressed():
    """Should parse uncompressed save game."""
    save_game = create_test_save_game(compressed=False)
    data = unparse_save_game(save_game)

    parsed = parse_save_game(data)

    assert parsed.header.is_compressed is False
    assert parsed.world["buildVersion"] == 123456
    assert parsed.settings["autoSaveCycleInterval"] == 10


def test_parse_save_game_version_mismatch_major():
    """Should raise error on major version mismatch."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_major_version = 6  # Wrong major version
    data = unparse_save_game(save_game)

    with pytest.raises(
        VersionMismatchError, match="Save version 6.35 is incompatible. Expected 7.35"
    ):
        parse_save_game(data, verify_version=True)


def test_parse_save_game_version_mismatch_minor():
    """Should raise error on minor version mismatch by default."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_minor_version = 30  # Wrong minor version
    data = unparse_save_game(save_game)

    with pytest.raises(
        VersionMismatchError, match="Save version 7.30 is incompatible. Expected 7.35"
    ):
        parse_save_game(data, verify_version=True)


def test_parse_save_game_allow_minor_mismatch():
    """Should allow minor version mismatch when requested."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_minor_version = 30
    data = unparse_save_game(save_game)

    parsed = parse_save_game(data, verify_version=True, allow_minor_mismatch=True)

    assert parsed.header.game_info.save_minor_version == 30


def test_parse_save_game_no_version_check():
    """Should skip version check when requested."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_major_version = 6
    data = unparse_save_game(save_game)

    parsed = parse_save_game(data, verify_version=False)

    assert parsed.header.game_info.save_major_version == 6


def test_parse_save_game_corrupted_compression():
    """Should raise error on corrupted compressed data."""
    save_game = create_test_save_game(compressed=True)
    data = bytearray(unparse_save_game(save_game))

    # Corrupt some bytes in the compressed section (near the end)
    corruption_start = len(data) - 50
    for i in range(corruption_start, corruption_start + 10):
        data[i] = 0xFF

    with pytest.raises(CorruptionError, match="Failed to decompress save body"):
        parse_save_game(bytes(data))


def test_parse_save_game_invalid_world_marker():
    """Should raise error on invalid world marker."""
    save_game = create_test_save_game()

    # Manually construct save with wrong world marker
    writer = BinaryWriter()
    from oni_save_parser.save_structure.header import unparse_header
    unparse_header(writer, save_game.header)
    unparse_templates(writer, save_game.templates)

    # Create body with wrong marker
    body_writer = BinaryWriter()
    body_writer.write_klei_string("invalid")  # Should be "world"

    if save_game.header.is_compressed:
        compressed = zlib.compress(body_writer.data, level=9, wbits=15)
        writer.write_bytes(compressed)
    else:
        writer.write_bytes(body_writer.data)

    with pytest.raises(CorruptionError, match='Expected "world" marker'):
        parse_save_game(writer.data)


def test_parse_save_game_invalid_world_type():
    """Should raise error on invalid world type name."""
    save_game = create_test_save_game()

    writer = BinaryWriter()
    from oni_save_parser.save_structure.header import unparse_header
    unparse_header(writer, save_game.header)
    unparse_templates(writer, save_game.templates)

    body_writer = BinaryWriter()
    body_writer.write_klei_string("world")
    body_writer.write_klei_string("InvalidType")  # Should be Klei.SaveFileRoot

    if save_game.header.is_compressed:
        compressed = zlib.compress(body_writer.data, level=9, wbits=15)
        writer.write_bytes(compressed)
    else:
        writer.write_bytes(body_writer.data)

    with pytest.raises(CorruptionError, match='Expected world type "Klei.SaveFileRoot"'):
        parse_save_game(writer.data)


def test_parse_save_game_invalid_settings_type():
    """Should raise error on invalid settings type name."""
    save_game = create_test_save_game()

    writer = BinaryWriter()
    from oni_save_parser.save_structure.header import unparse_header
    unparse_header(writer, save_game.header)
    unparse_templates(writer, save_game.templates)

    body_writer = BinaryWriter()
    body_writer.write_klei_string("world")
    body_writer.write_klei_string("Klei.SaveFileRoot")

    # Write minimal world data
    from oni_save_parser.save_structure.type_templates import unparse_by_template
    unparse_by_template(body_writer, save_game.templates, "Klei.SaveFileRoot", save_game.world)

    # Write invalid settings type
    body_writer.write_klei_string("InvalidSettings")  # Should be Game+Settings

    if save_game.header.is_compressed:
        compressed = zlib.compress(body_writer.data, level=9, wbits=15)
        writer.write_bytes(compressed)
    else:
        writer.write_bytes(body_writer.data)

    with pytest.raises(CorruptionError, match='Expected settings type "Game\\+Settings"'):
        parse_save_game(writer.data)


def test_parse_save_game_invalid_ksav_marker():
    """Should raise error on invalid KSAV marker."""
    save_game = create_test_save_game()

    writer = BinaryWriter()
    from oni_save_parser.save_structure.header import unparse_header
    unparse_header(writer, save_game.header)
    unparse_templates(writer, save_game.templates)

    body_writer = BinaryWriter()
    body_writer.write_klei_string("world")
    body_writer.write_klei_string("Klei.SaveFileRoot")

    from oni_save_parser.save_structure.type_templates import unparse_by_template
    unparse_by_template(body_writer, save_game.templates, "Klei.SaveFileRoot", save_game.world)

    body_writer.write_klei_string("Game+Settings")
    unparse_by_template(body_writer, save_game.templates, "Game+Settings", save_game.settings)

    # Write sim data
    body_writer.write_int32(len(save_game.sim_data))
    body_writer.write_bytes(save_game.sim_data)

    # Write invalid KSAV marker
    body_writer.write_chars("XXXX")  # Should be "KSAV"

    if save_game.header.is_compressed:
        compressed = zlib.compress(body_writer.data, level=9, wbits=15)
        writer.write_bytes(compressed)
    else:
        writer.write_bytes(body_writer.data)

    with pytest.raises(CorruptionError, match='Expected "KSAV" marker'):
        parse_save_game(writer.data)


def test_round_trip_save_game_compressed():
    """Should round-trip compressed save game."""
    original = create_test_save_game(compressed=True)

    # Write
    data = unparse_save_game(original)

    # Read
    parsed = parse_save_game(data, verify_version=False)

    # Verify all fields
    assert parsed.header.build_version == original.header.build_version
    assert parsed.header.is_compressed == original.header.is_compressed
    assert len(parsed.templates) == len(original.templates)
    assert parsed.world == original.world
    assert parsed.settings == original.settings
    assert parsed.sim_data == original.sim_data
    assert parsed.version_major == original.version_major
    assert parsed.version_minor == original.version_minor
    assert len(parsed.game_objects) == len(original.game_objects)
    assert parsed.game_data == original.game_data


def test_round_trip_save_game_uncompressed():
    """Should round-trip uncompressed save game."""
    original = create_test_save_game(compressed=False)

    # Write
    data = unparse_save_game(original)

    # Read
    parsed = parse_save_game(data, verify_version=False)

    # Verify
    assert parsed.header.is_compressed is False
    assert parsed.world == original.world
    assert parsed.settings == original.settings


def test_save_game_with_empty_sim_data():
    """Should handle empty sim data."""
    save_game = create_test_save_game()
    save_game.sim_data = b""

    data = unparse_save_game(save_game)
    parsed = parse_save_game(data, verify_version=False)

    assert parsed.sim_data == b""


def test_save_game_with_large_sim_data():
    """Should handle large sim data."""
    save_game = create_test_save_game()
    save_game.sim_data = b"\x42" * 10000  # 10KB of data

    data = unparse_save_game(save_game)
    parsed = parse_save_game(data, verify_version=False)

    assert len(parsed.sim_data) == 10000
    assert parsed.sim_data == save_game.sim_data
