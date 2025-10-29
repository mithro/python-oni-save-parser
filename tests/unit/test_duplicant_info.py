"""Tests for duplicant_info example script."""

import subprocess
import sys
from pathlib import Path

import pytest
from oni_save_parser.save_structure import SaveGame, unparse_save_game
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectBehavior,
    GameObjectGroup,
    Quaternion,
    Vector3,
)
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_save_with_duplicants(path: Path) -> None:
    """Create a test save file with duplicant objects."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=3,
        base_name="Dup Test",
        is_auto_save=False,
        original_save_name="Dup Test Cycle 100",
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

    # Create duplicant object with behaviors
    dup_obj = GameObject(
        position=Vector3(x=100.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[dup_obj] * 3),
        GameObjectGroup(prefab_name="Tile", objects=[dup_obj] * 10),
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


def test_duplicant_info_help():
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Extract duplicant information" in result.stdout


def test_duplicant_info_list_duplicants(tmp_path: Path):
    """Should list all duplicants."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Found 3 duplicants" in result.stdout or "3 duplicants" in result.stdout.lower()
