"""Tests for colony_scanner.py example script."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from oni_save_parser import save_to_file
from oni_save_parser.save_structure import (
    SaveGame,
    SaveGameHeader,
    SaveGameInfo,
)
from oni_save_parser.save_structure.type_templates import (
    TypeInfo,
    TypeTemplate,
    TypeTemplateMember,
)


def create_test_save(
    path: Path,
    colony_name: str = "Test Colony",
    cycle: int = 100,
    duplicant_count: int = 5,
) -> None:
    """Create a minimal test save file.

    Args:
        path: Path to save file
        colony_name: Colony name
        cycle: Cycle number
        duplicant_count: Number of duplicants
    """
    game_info = SaveGameInfo(
        number_of_cycles=cycle,
        number_of_duplicants=duplicant_count,
        base_name=colony_name,
        is_auto_save=False,
        original_save_name=path.name,
        save_major_version=7,
        save_minor_version=35,
        cluster_id="SNDST-A",
        sandbox_enabled=False,
        colony_guid="test-guid-123",
        dlc_id="",
    )

    header = SaveGameHeader(
        build_version=654321,
        header_version=1,
        is_compressed=False,
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

    save = SaveGame(
        header=header,
        templates=templates,
        world={"buildVersion": 654321},
        settings={"difficulty": 2},
        sim_data=b"",
        version_major=7,
        version_minor=35,
        game_objects=[],
        game_data=b"",
    )

    save_to_file(save, path)


def test_colony_scanner_help() -> None:
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/colony_scanner.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "scan" in result.stdout.lower() or "colony" in result.stdout.lower()


def test_colony_scanner_custom_directory(tmp_path: Path) -> None:
    """Should scan custom directory for save files."""
    # Create some test save files
    save_dir = tmp_path / "saves"
    save_dir.mkdir()

    # We'll need to create actual save files for this test
    # For now, test that the script accepts the argument
    result = subprocess.run(
        [sys.executable, "examples/colony_scanner.py", str(save_dir)],
        capture_output=True,
        text=True,
    )
    # Should succeed even with no saves
    assert result.returncode == 0


def test_colony_scanner_finds_saves(tmp_path: Path) -> None:
    """Should find and list save files."""
    save_dir = tmp_path / "saves"
    save_dir.mkdir()

    # Create test saves
    create_test_save(save_dir / "Colony1.sav", "Alpha Base", 100, 8)
    create_test_save(save_dir / "Colony2.sav", "Beta Base", 250, 12)

    result = subprocess.run(
        [sys.executable, "examples/colony_scanner.py", str(save_dir)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Alpha Base" in result.stdout
    assert "Beta Base" in result.stdout
    assert "100" in result.stdout
    assert "250" in result.stdout


def test_colony_scanner_json_output(tmp_path: Path) -> None:
    """Should output JSON format."""
    save_dir = tmp_path / "saves"
    save_dir.mkdir()

    # Create test save
    create_test_save(save_dir / "TestColony.sav", "Test Colony", 42, 5)

    result = subprocess.run(
        [sys.executable, "examples/colony_scanner.py", str(save_dir), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Parse JSON output
    data = json.loads(result.stdout)

    assert len(data) == 1
    assert data[0]["colony_name"] == "Test Colony"
    assert data[0]["cycle"] == 42
    assert data[0]["duplicants"] == 5
    assert data[0]["file"] == "TestColony.sav"


def test_colony_scanner_empty_directory(tmp_path: Path) -> None:
    """Should handle empty directory gracefully."""
    save_dir = tmp_path / "empty"
    save_dir.mkdir()

    result = subprocess.run(
        [sys.executable, "examples/colony_scanner.py", str(save_dir)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Total: 0 save files" in result.stdout
