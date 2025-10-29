"""Tests for save file header parsing."""

import json

import pytest
from oni_save_parser.parser.errors import CorruptionError
from oni_save_parser.parser.parse import BinaryParser
from oni_save_parser.parser.unparse import BinaryWriter
from oni_save_parser.save_structure.header import (
    SaveGameHeader,
    SaveGameInfo,
    parse_header,
    unparse_header,
)


def test_save_game_info_to_dict():
    """Should convert SaveGameInfo to dictionary."""
    info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=5,
        base_name="MyBase",
        is_auto_save=False,
        original_save_name="MyBase Cycle 100",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="12345678-1234-1234-1234-123456789012",
        dlc_id="",
    )

    data = info.to_dict()

    assert data["numberOfCycles"] == 100
    assert data["numberOfDuplicants"] == 5
    assert data["baseName"] == "MyBase"
    assert data["isAutoSave"] is False


def test_save_game_info_from_dict():
    """Should create SaveGameInfo from dictionary."""
    data = {
        "numberOfCycles": 100,
        "numberOfDuplicants": 5,
        "baseName": "MyBase",
        "isAutoSave": False,
        "originalSaveName": "MyBase Cycle 100",
        "saveMajorVersion": 7,
        "saveMinorVersion": 35,
        "clusterId": "vanilla",
        "sandboxEnabled": False,
        "colonyGuid": "12345678-1234-1234-1234-123456789012",
        "dlcId": "",
    }

    info = SaveGameInfo.from_dict(data)

    assert info.number_of_cycles == 100
    assert info.number_of_duplicants == 5
    assert info.base_name == "MyBase"
    assert info.is_auto_save is False


def test_parse_header_version_0():
    """Should parse header version 0 (no compression flag)."""
    game_info = {
        "numberOfCycles": 50,
        "numberOfDuplicants": 3,
        "baseName": "TestBase",
        "isAutoSave": True,
        "originalSaveName": "TestBase Cycle 50",
        "saveMajorVersion": 7,
        "saveMinorVersion": 30,
        "clusterId": "vanilla",
        "sandboxEnabled": True,
        "colonyGuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "dlcId": "",
    }
    game_info_json = json.dumps(game_info)
    game_info_bytes = game_info_json.encode("utf-8")

    writer = BinaryWriter()
    writer.write_uint32(123456)  # build version
    writer.write_uint32(len(game_info_bytes))  # header size
    writer.write_uint32(0)  # header version
    # No compression flag for version 0
    writer.write_bytes(game_info_bytes)

    parser = BinaryParser(writer.data)
    header = parse_header(parser)

    assert header.build_version == 123456
    assert header.header_version == 0
    assert header.is_compressed is False
    assert header.game_info.number_of_cycles == 50
    assert header.game_info.base_name == "TestBase"


def test_parse_header_version_1_uncompressed():
    """Should parse header version 1 with compression flag false."""
    game_info = {
        "numberOfCycles": 100,
        "numberOfDuplicants": 5,
        "baseName": "MyBase",
        "isAutoSave": False,
        "originalSaveName": "MyBase Cycle 100",
        "saveMajorVersion": 7,
        "saveMinorVersion": 35,
        "clusterId": "vanilla",
        "sandboxEnabled": False,
        "colonyGuid": "12345678-1234-1234-1234-123456789012",
        "dlcId": "",
    }
    game_info_json = json.dumps(game_info)
    game_info_bytes = game_info_json.encode("utf-8")

    writer = BinaryWriter()
    writer.write_uint32(555555)  # build version
    writer.write_uint32(len(game_info_bytes))  # header size
    writer.write_uint32(1)  # header version
    writer.write_uint32(0)  # not compressed
    writer.write_bytes(game_info_bytes)

    parser = BinaryParser(writer.data)
    header = parse_header(parser)

    assert header.build_version == 555555
    assert header.header_version == 1
    assert header.is_compressed is False
    assert header.game_info.number_of_cycles == 100


def test_parse_header_version_1_compressed():
    """Should parse header version 1 with compression flag true."""
    game_info = {
        "numberOfCycles": 200,
        "numberOfDuplicants": 10,
        "baseName": "CompressedBase",
        "isAutoSave": False,
        "originalSaveName": "CompressedBase Cycle 200",
        "saveMajorVersion": 7,
        "saveMinorVersion": 35,
        "clusterId": "vanilla",
        "sandboxEnabled": False,
        "colonyGuid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "dlcId": "EXPANSION1_ID",
    }
    game_info_json = json.dumps(game_info)
    game_info_bytes = game_info_json.encode("utf-8")

    writer = BinaryWriter()
    writer.write_uint32(666666)  # build version
    writer.write_uint32(len(game_info_bytes))  # header size
    writer.write_uint32(1)  # header version
    writer.write_uint32(1)  # compressed
    writer.write_bytes(game_info_bytes)

    parser = BinaryParser(writer.data)
    header = parse_header(parser)

    assert header.build_version == 666666
    assert header.header_version == 1
    assert header.is_compressed is True
    assert header.game_info.dlc_id == "EXPANSION1_ID"


def test_parse_header_invalid_json():
    """Should raise error on invalid JSON."""
    invalid_json = b"{ invalid json }"

    writer = BinaryWriter()
    writer.write_uint32(123456)
    writer.write_uint32(len(invalid_json))
    writer.write_uint32(1)
    writer.write_uint32(0)
    writer.write_bytes(invalid_json)

    parser = BinaryParser(writer.data)

    with pytest.raises(CorruptionError, match="Failed to parse game info JSON"):
        parse_header(parser)


def test_unparse_header_version_0():
    """Should write header version 0."""
    game_info = SaveGameInfo(
        number_of_cycles=50,
        number_of_duplicants=3,
        base_name="TestBase",
        is_auto_save=True,
        original_save_name="TestBase Cycle 50",
        save_major_version=7,
        save_minor_version=30,
        cluster_id="vanilla",
        sandbox_enabled=True,
        colony_guid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        dlc_id="",
    )
    header = SaveGameHeader(
        build_version=123456, header_version=0, is_compressed=False, game_info=game_info
    )

    writer = BinaryWriter()
    unparse_header(writer, header)

    # Parse back and verify
    parser = BinaryParser(writer.data)
    parsed = parse_header(parser)

    assert parsed.build_version == 123456
    assert parsed.header_version == 0
    assert parsed.is_compressed is False
    assert parsed.game_info.base_name == "TestBase"


def test_unparse_header_version_1():
    """Should write header version 1 with compression flag."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=5,
        base_name="MyBase",
        is_auto_save=False,
        original_save_name="MyBase Cycle 100",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="12345678-1234-1234-1234-123456789012",
        dlc_id="",
    )
    header = SaveGameHeader(
        build_version=555555, header_version=1, is_compressed=True, game_info=game_info
    )

    writer = BinaryWriter()
    unparse_header(writer, header)

    # Parse back and verify
    parser = BinaryParser(writer.data)
    parsed = parse_header(parser)

    assert parsed.build_version == 555555
    assert parsed.header_version == 1
    assert parsed.is_compressed is True
    assert parsed.game_info.number_of_cycles == 100


def test_round_trip_header():
    """Should round-trip header."""
    original_info = SaveGameInfo(
        number_of_cycles=150,
        number_of_duplicants=8,
        base_name="RoundTripBase",
        is_auto_save=False,
        original_save_name="RoundTripBase Cycle 150",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=True,
        colony_guid="cccccccc-cccc-cccc-cccc-cccccccccccc",
        dlc_id="EXPANSION1_ID",
    )
    original = SaveGameHeader(
        build_version=777777, header_version=1, is_compressed=True, game_info=original_info
    )

    # Write
    writer = BinaryWriter()
    unparse_header(writer, original)

    # Read
    parser = BinaryParser(writer.data)
    parsed = parse_header(parser)

    # Verify all fields
    assert parsed.build_version == original.build_version
    assert parsed.header_version == original.header_version
    assert parsed.is_compressed == original.is_compressed
    assert parsed.game_info.number_of_cycles == original.game_info.number_of_cycles
    assert parsed.game_info.number_of_duplicants == original.game_info.number_of_duplicants
    assert parsed.game_info.base_name == original.game_info.base_name
    assert parsed.game_info.is_auto_save == original.game_info.is_auto_save
    assert parsed.game_info.dlc_id == original.game_info.dlc_id
