"""Tests for resource_counter example script."""

import json
import subprocess
import sys
from pathlib import Path

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
            name="PrimaryElement",
            fields=[
                TypeTemplateMember(name="Mass", type=TypeInfo(info=10)),
                TypeTemplateMember(name="Temperature", type=TypeInfo(info=10)),
            ],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555}
    settings = {"difficulty": 2}

    # Storage container with 500kg at 293.15K (StorageLocker prefab)
    storage_locker = GameObject(
        position=Vector3(x=10.0, y=5.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "Mass": 500.0,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    # Liquid reservoir with 1000kg at 293.15K
    liquid_reservoir = GameObject(
        position=Vector3(x=15.0, y=5.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "Mass": 1000.0,
                    "Temperature": 293.15,
                },
                extra_data=None,
                extra_raw=b"",
            ),
        ],
    )

    # Loose debris - 25.5kg at 293.15K
    iron_ore = GameObject(
        position=Vector3(x=20.0, y=8.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="PrimaryElement",
                template_data={
                    "Mass": 25.5,
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
        sim_data=b"\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)



def test_create_save_with_resources_fixture(tmp_path: Path) -> None:
    """Verify fixture creates valid save file."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0


def test_resource_counter_help() -> None:
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Count resources" in result.stdout or "resource" in result.stdout.lower()


def test_resource_counter_finds_storage(tmp_path: Path) -> None:
    """Should find storage containers."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Should find the StorageLocker and LiquidReservoir from fixture
    assert "Storage" in result.stdout or "storage" in result.stdout


def test_resource_counter_finds_debris(tmp_path: Path) -> None:
    """Should find loose debris."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Should find the IronOre debris from fixture (25.5kg)
    assert "debris" in result.stdout.lower() or "IronOre" in result.stdout


def test_resource_counter_duplicant_detection(tmp_path: Path) -> None:
    """Should detect duplicant inventories (currently no duplicants in fixture)."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Fixture has no duplicants, so duplicants section should not appear in table output
    # But we should still see storage and debris sections
    assert "STORAGE CONTAINERS:" in result.stdout or "Storage" in result.stdout
    assert "DEBRIS" in result.stdout or "debris" in result.stdout.lower()


def test_resource_counter_json_output(tmp_path: Path) -> None:
    """Should output resources as JSON."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    data = json.loads(result.stdout)

    # Should have storage, debris, and duplicants sections
    assert "storage" in data
    assert "debris" in data
    assert "duplicants" in data

    # Verify storage has 2 containers
    assert len(data["storage"]) == 2


def test_resource_counter_table_output(tmp_path: Path) -> None:
    """Should display resources in ASCII table format."""
    save_path = tmp_path / "test.sav"
    create_save_with_resources(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    # Check for table headers
    assert "Type" in result.stdout or "Prefab" in result.stdout
    assert "Mass" in result.stdout
    assert "---" in result.stdout  # Table separator line
