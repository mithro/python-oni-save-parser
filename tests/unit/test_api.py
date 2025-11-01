"""Tests for high-level API functions."""

from pathlib import Path

import pytest

from oni_save_parser import (
    get_colony_info,
    get_game_objects_by_prefab,
    get_prefab_counts,
    list_prefab_types,
    load_save_file,
    save_to_file,
)
from oni_save_parser.parser.errors import VersionMismatchError
from oni_save_parser.save_structure import SaveGame
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectGroup,
    Quaternion,
    Vector3,
)
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_test_save_game() -> SaveGame:
    """Create a test SaveGame for API testing."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=5,
        base_name="TestBase",
        is_auto_save=False,
        original_save_name="TestBase Cycle 100",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="12345678-1234-1234-1234-123456789012",
        dlc_id="EXPANSION1_ID",
    )
    header = SaveGameHeader(
        build_version=555555,
        header_version=1,
        is_compressed=True,
        game_info=game_info,
    )

    # Minimal templates
    templates = [
        TypeTemplate(
            name="Klei.SaveFileRoot",
            fields=[
                TypeTemplateMember(name="buildVersion", type=TypeInfo(info=6)),
                TypeTemplateMember(name="worldID", type=TypeInfo(info=12)),
            ],
            properties=[],
        ),
        TypeTemplate(
            name="Game+Settings",
            fields=[
                TypeTemplateMember(name="difficulty", type=TypeInfo(info=6)),
            ],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555, "worldID": "TestWorld"}
    settings = {"difficulty": 1}

    # Create test game objects
    minion_obj = GameObject(
        position=Vector3(x=10.0, y=20.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    tile_obj = GameObject(
        position=Vector3(x=5.0, y=10.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[minion_obj] * 5),
        GameObjectGroup(prefab_name="Tile", objects=[tile_obj] * 100),
        GameObjectGroup(prefab_name="Door", objects=[tile_obj] * 10),
    ]

    return SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=b"\x01\x02\x03\x04\x05",
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )


def test_load_save_file_success(tmp_path: Path) -> None:
    """Should load save file from disk."""
    save_game = create_test_save_game()
    save_path = tmp_path / "test.sav"

    # Write test file
    from oni_save_parser.save_structure import unparse_save_game

    data = unparse_save_game(save_game)
    save_path.write_bytes(data)

    # Load it back
    loaded = load_save_file(save_path)

    assert loaded.header.game_info.base_name == "TestBase"
    assert loaded.header.game_info.number_of_cycles == 100


def test_load_save_file_not_found() -> None:
    """Should raise FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_save_file("nonexistent.sav")


def test_load_save_file_version_mismatch(tmp_path: Path) -> None:
    """Should raise VersionMismatchError for incompatible version."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_major_version = 6
    save_path = tmp_path / "test.sav"

    from oni_save_parser.save_structure import unparse_save_game

    data = unparse_save_game(save_game)
    save_path.write_bytes(data)

    with pytest.raises(VersionMismatchError):
        load_save_file(save_path, verify_version=True, allow_minor_mismatch=False)


def test_load_save_file_allow_minor_mismatch(tmp_path: Path) -> None:
    """Should allow minor version mismatch when requested."""
    save_game = create_test_save_game()
    save_game.header.game_info.save_minor_version = 30
    save_path = tmp_path / "test.sav"

    from oni_save_parser.save_structure import unparse_save_game

    data = unparse_save_game(save_game)
    save_path.write_bytes(data)

    loaded = load_save_file(save_path, verify_version=True, allow_minor_mismatch=True)
    assert loaded.header.game_info.save_minor_version == 30


def test_save_to_file(tmp_path: Path) -> None:
    """Should write SaveGame to disk."""
    save_game = create_test_save_game()
    save_path = tmp_path / "output.sav"

    save_to_file(save_game, save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0

    # Verify we can load it back
    loaded = load_save_file(save_path)
    assert loaded.header.game_info.base_name == save_game.header.game_info.base_name


def test_save_to_file_with_string_path(tmp_path: Path) -> None:
    """Should accept string path."""
    save_game = create_test_save_game()
    save_path = str(tmp_path / "output.sav")

    save_to_file(save_game, save_path)

    assert Path(save_path).exists()


def test_get_colony_info() -> None:
    """Should extract colony information."""
    save_game = create_test_save_game()
    info = get_colony_info(save_game)

    assert info["colony_name"] == "TestBase"
    assert info["cycle"] == 100
    assert info["duplicant_count"] == 5
    assert info["cluster_id"] == "vanilla"
    assert info["dlc_id"] == "EXPANSION1_ID"
    assert info["is_auto_save"] is False
    assert info["sandbox_enabled"] is False
    assert info["save_version"] == "7.35"
    assert info["build_version"] == 555555
    assert info["compressed"] is True


def test_get_game_objects_by_prefab() -> None:
    """Should get game objects by prefab name."""
    save_game = create_test_save_game()

    minions = get_game_objects_by_prefab(save_game, "Minion")
    assert len(minions) == 5

    tiles = get_game_objects_by_prefab(save_game, "Tile")
    assert len(tiles) == 100

    doors = get_game_objects_by_prefab(save_game, "Door")
    assert len(doors) == 10


def test_get_game_objects_by_prefab_not_found() -> None:
    """Should return empty list for non-existent prefab."""
    save_game = create_test_save_game()

    result = get_game_objects_by_prefab(save_game, "NonExistent")
    assert result == []


def test_list_prefab_types() -> None:
    """Should list all prefab types."""
    save_game = create_test_save_game()

    prefabs = list_prefab_types(save_game)

    assert len(prefabs) == 3
    assert "Minion" in prefabs
    assert "Tile" in prefabs
    assert "Door" in prefabs


def test_list_prefab_types_empty() -> None:
    """Should return empty list for save with no game objects."""
    save_game = create_test_save_game()
    save_game.game_objects = []

    prefabs = list_prefab_types(save_game)
    assert prefabs == []


def test_get_prefab_counts() -> None:
    """Should get counts for each prefab type."""
    save_game = create_test_save_game()

    counts = get_prefab_counts(save_game)

    assert counts["Minion"] == 5
    assert counts["Tile"] == 100
    assert counts["Door"] == 10
    assert len(counts) == 3


def test_get_prefab_counts_empty() -> None:
    """Should return empty dict for save with no game objects."""
    save_game = create_test_save_game()
    save_game.game_objects = []

    counts = get_prefab_counts(save_game)
    assert counts == {}


def test_round_trip_through_file(tmp_path: Path) -> None:
    """Should maintain data through save and load cycle."""
    original = create_test_save_game()
    save_path = tmp_path / "round_trip.sav"

    # Save
    save_to_file(original, save_path)

    # Load
    loaded = load_save_file(save_path)

    # Verify key fields
    assert loaded.header.game_info.base_name == original.header.game_info.base_name
    assert loaded.header.game_info.number_of_cycles == original.header.game_info.number_of_cycles
    assert len(loaded.game_objects) == len(original.game_objects)

    # Verify game objects
    loaded_counts = get_prefab_counts(loaded)
    original_counts = get_prefab_counts(original)
    assert loaded_counts == original_counts
