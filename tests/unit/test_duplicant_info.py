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
        TypeTemplate(
            name="MinionIdentity",
            fields=[
                TypeTemplateMember(name="name", type=TypeInfo(info=12)),
                TypeTemplateMember(name="nameStringKey", type=TypeInfo(info=12)),
                TypeTemplateMember(name="gender", type=TypeInfo(info=12)),
                TypeTemplateMember(name="genderStringKey", type=TypeInfo(info=12)),
                TypeTemplateMember(name="personalityResourceId", type=TypeInfo(info=12)),
                TypeTemplateMember(name="voicePitch", type=TypeInfo(info=10)),
            ],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555}
    settings = {"difficulty": 2}

    # Create duplicants with MinionIdentity behavior
    dup1 = GameObject(
        position=Vector3(x=100.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Meep",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.MEEP",
                    "gender": "NB",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.NB",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_LONER",
                    "voicePitch": 1.0,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    dup2 = GameObject(
        position=Vector3(x=110.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Devon",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.DEVON",
                    "gender": "M",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.M",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_BUILDER",
                    "voicePitch": 0.8,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    dup3 = GameObject(
        position=Vector3(x=120.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Catalina",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.CATALINA",
                    "gender": "F",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.F",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_RESEARCHER",
                    "voicePitch": 1.2,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[dup1, dup2, dup3]),
        GameObjectGroup(prefab_name="Tile", objects=[GameObject(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
            scale=Vector3(x=1.0, y=1.0, z=1.0),
            folder=0,
            behaviors=[],
        )] * 10),
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


def test_duplicant_info_shows_names(tmp_path: Path):
    """Should show duplicant names."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Meep" in result.stdout
    assert "Devon" in result.stdout
    assert "Catalina" in result.stdout


def test_duplicant_info_json_output(tmp_path: Path):
    """Should output duplicant info as JSON."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    import json
    data = json.loads(result.stdout)

    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["name"] == "Meep"
    assert data[1]["name"] == "Devon"
    assert data[2]["name"] == "Catalina"
