"""Tests for resource_counter example script."""

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


def create_save_with_resources(path: Path) -> None:
    """Create a test save file with various resource-containing objects."""
    game_info = SaveGameInfo(
        number_of_cycles=50,
        number_of_duplicants=1,
        base_name="Resource Test",
        is_auto_save=False,
        original_save_name="Resource Test Cycle 50",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
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
            name="Storage",
            fields=[
                TypeTemplateMember(name="items", type=TypeInfo(info=23)),
                TypeTemplateMember(name="capacityKg", type=TypeInfo(info=10)),
            ],
            properties=[],
        ),
        TypeTemplate(
            name="PrimaryElement",
            fields=[
                TypeTemplateMember(name="ElementID", type=TypeInfo(info=7)),
                TypeTemplateMember(name="Mass", type=TypeInfo(info=10)),
                TypeTemplateMember(name="Temperature", type=TypeInfo(info=10)),
            ],
            properties=[],
        ),
        TypeTemplate(
            name="Pickupable",
            fields=[
                TypeTemplateMember(name="absorbable", type=TypeInfo(info=3)),
                TypeTemplateMember(name="isChoreAllowedCb", type=TypeInfo(info=12)),
            ],
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

    # Storage container with Iron (StorageLocker prefab)
    storage_locker = GameObject(
        position=Vector3(x=10.0, y=5.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="Storage",
                template_data={
                    "items": [],
                    "capacityKg": 20000.0,
                },
                extra_data=None,
                extra_raw=b"",
            ),
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "ElementID": 1,  # Iron
                    "Mass": 500.0,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    # Storage container with Water (LiquidReservoir prefab)
    liquid_reservoir = GameObject(
        position=Vector3(x=15.0, y=5.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="Storage",
                template_data={
                    "items": [],
                    "capacityKg": 5000.0,
                },
                extra_data=None,
                extra_raw=b"",
            ),
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "ElementID": 2,  # Water
                    "Mass": 1000.0,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    # Loose debris - IronOre with Pickupable behavior
    iron_ore = GameObject(
        position=Vector3(x=20.0, y=8.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "ElementID": 3,  # IronOre
                    "Mass": 25.5,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
            GameObjectBehavior(
                name="Pickupable",
                template_data={
                    "absorbable": True,
                    "isChoreAllowedCb": "",
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    # Duplicant "Meep" carrying Copper
    duplicant = GameObject(
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
            ),
            GameObjectBehavior(
                name="Storage",
                template_data={
                    "items": [],
                    "capacityKg": 400.0,
                },
                extra_data=None,
                extra_raw=b"",
            ),
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "ElementID": 4,  # Copper
                    "Mass": 10.0,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    game_objects = [
        GameObjectGroup(prefab_name="StorageLocker", objects=[storage_locker]),
        GameObjectGroup(prefab_name="LiquidReservoir", objects=[liquid_reservoir]),
        GameObjectGroup(prefab_name="IronOre", objects=[iron_ore]),
        GameObjectGroup(prefab_name="Minion", objects=[duplicant]),
    ]

    save_game = SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=b"\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)



def test_resource_counter_help():
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Count resources" in result.stdout or "resource" in result.stdout.lower()
