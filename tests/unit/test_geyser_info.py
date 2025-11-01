"""Tests for geyser_info example script."""

import subprocess
import sys
from pathlib import Path

import pytest

from oni_save_parser.save_structure import SaveGame, unparse_save_game
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectGroup,
    Quaternion,
    Vector3,
)
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_save_with_geysers(path: Path) -> None:
    """Create a test save file with geyser objects."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=5,
        base_name="Geyser Test",
        is_auto_save=False,
        original_save_name="Geyser Test Cycle 100",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        dlc_id="",
    )
    header = SaveGameHeader(
        build_version=555555,
        header_version=1,
        is_compressed=True,
        game_info=game_info,
    )

    templates = [
        TypeTemplate(
            name="Klei.SaveFileRoot",
            fields=[TypeTemplateMember(name="buildVersion", type=TypeInfo(info=6))],
            properties=[],
        ),
        TypeTemplate(
            name="Game+Settings",
            fields=[TypeTemplateMember(name="difficulty", type=TypeInfo(info=6))],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555}
    settings = {"difficulty": 2}

    # Create geyser objects
    geyser_obj = GameObject(
        position=Vector3(x=100.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="GeyserGeneric_steam", objects=[geyser_obj] * 2),
        GameObjectGroup(prefab_name="GeyserGeneric_hot_co2", objects=[geyser_obj]),
        GameObjectGroup(prefab_name="Tile", objects=[geyser_obj] * 10),
    ]

    save_game = SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=b"\\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)


def test_geyser_info_help() -> None:
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Extract geyser information" in result.stdout


def test_geyser_info_list_prefabs(tmp_path: Path) -> None:
    """Should list geyser prefabs."""
    save_path = tmp_path / "test.sav"
    create_save_with_geysers(save_path)

    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", str(save_path), "--list-prefabs"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "GeyserGeneric_steam" in result.stdout
    assert "GeyserGeneric_hot_co2" in result.stdout


def test_geyser_info_text_output(tmp_path: Path) -> None:
    """Should display geyser information in text format."""
    save_path = tmp_path / "test.sav"
    create_save_with_geysers(save_path)

    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "GeyserGeneric_steam" in result.stdout
    assert "GeyserGeneric_hot_co2" in result.stdout
    assert "Total geysers: 3" in result.stdout


def test_geyser_info_json_output(tmp_path: Path) -> None:
    """Should display geyser information in JSON format."""
    save_path = tmp_path / "test.sav"
    create_save_with_geysers(save_path)

    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", str(save_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    import json

    data = json.loads(result.stdout)
    assert "GeyserGeneric_steam" in data
    assert "GeyserGeneric_hot_co2" in data
    assert len(data["GeyserGeneric_steam"]) == 2
    assert len(data["GeyserGeneric_hot_co2"]) == 1


def test_geyser_info_filter_prefab(tmp_path: Path) -> None:
    """Should filter to specific prefab type."""
    save_path = tmp_path / "test.sav"
    create_save_with_geysers(save_path)

    result = subprocess.run(
        [
            sys.executable,
            "examples/geyser_info.py",
            str(save_path),
            "--prefab",
            "GeyserGeneric_steam",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "GeyserGeneric_steam" in result.stdout
    assert "GeyserGeneric_hot_co2" not in result.stdout


def test_geyser_info_file_not_found() -> None:
    """Should handle missing file gracefully."""
    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", "nonexistent.sav"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Error" in result.stderr


def test_geyser_info_invalid_prefab(tmp_path: Path) -> None:
    """Should handle invalid prefab filter."""
    save_path = tmp_path / "test.sav"
    create_save_with_geysers(save_path)

    result = subprocess.run(
        [
            sys.executable,
            "examples/geyser_info.py",
            str(save_path),
            "--prefab",
            "NonExistentGeyser",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr


def test_geyser_info_compact_format() -> None:
    """Test geyser_info.py with compact format."""
    # Use smallest test save
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        pytest.skip("Test save not found")

    result = subprocess.run(
        [sys.executable, "examples/geyser_info.py", str(save_path), "--format", "compact"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "kg/s avg" in result.stdout
    assert "erupting" in result.stdout
