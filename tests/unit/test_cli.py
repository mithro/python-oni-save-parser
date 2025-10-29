"""Tests for CLI tool."""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from oni_save_parser.__main__ import cmd_info, cmd_prefabs, main
from oni_save_parser.save_structure import SaveGame
from oni_save_parser.save_structure.game_objects import GameObject, GameObjectGroup, Quaternion, Vector3
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_test_save_file(path: Path) -> None:
    """Create a test save file at the given path."""
    game_info = SaveGameInfo(
        number_of_cycles=150,
        number_of_duplicants=8,
        base_name="CLI Test Base",
        is_auto_save=False,
        original_save_name="CLI Test Base Cycle 150",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=True,
        colony_guid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        dlc_id="",
    )
    header = SaveGameHeader(
        build_version=666666,
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

    world = {"buildVersion": 666666}
    settings = {"difficulty": 2}

    # Create game objects
    minion = GameObject(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[minion] * 8),
        GameObjectGroup(prefab_name="Tile", objects=[minion] * 500),
        GameObjectGroup(prefab_name="Door", objects=[minion] * 20),
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

    from oni_save_parser.save_structure import unparse_save_game

    data = unparse_save_game(save_game)
    path.write_bytes(data)


def test_cmd_info_text_output(tmp_path: Path, capsys):
    """Should display colony info in text format."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(file=save_path, json=False, allow_minor_mismatch=True)

    result = cmd_info(args)

    assert result == 0

    captured = capsys.readouterr()
    assert "CLI Test Base" in captured.out
    assert "Cycle: 150" in captured.out
    assert "Duplicants: 8" in captured.out
    assert "Sandbox: True" in captured.out


def test_cmd_info_json_output(tmp_path: Path, capsys):
    """Should display colony info in JSON format."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(file=save_path, json=True, allow_minor_mismatch=True)

    result = cmd_info(args)

    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["colony_name"] == "CLI Test Base"
    assert data["cycle"] == 150
    assert data["duplicant_count"] == 8
    assert data["sandbox_enabled"] is True


def test_cmd_info_file_not_found(tmp_path: Path, capsys):
    """Should handle missing file gracefully."""
    import argparse

    args = argparse.Namespace(
        file=tmp_path / "nonexistent.sav", json=False, allow_minor_mismatch=True
    )

    result = cmd_info(args)

    assert result == 1

    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_cmd_prefabs_list(tmp_path: Path, capsys):
    """Should list prefab types."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(
        file=save_path, counts=False, json=False, allow_minor_mismatch=True
    )

    result = cmd_prefabs(args)

    assert result == 0

    captured = capsys.readouterr()
    assert "Door" in captured.out
    assert "Minion" in captured.out
    assert "Tile" in captured.out


def test_cmd_prefabs_with_counts(tmp_path: Path, capsys):
    """Should show prefab counts."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(
        file=save_path, counts=True, json=False, allow_minor_mismatch=True
    )

    result = cmd_prefabs(args)

    assert result == 0

    captured = capsys.readouterr()
    assert "Door: 20" in captured.out
    assert "Minion: 8" in captured.out
    assert "Tile: 500" in captured.out


def test_cmd_prefabs_json_list(tmp_path: Path, capsys):
    """Should output prefab list as JSON."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(
        file=save_path, counts=False, json=True, allow_minor_mismatch=True
    )

    result = cmd_prefabs(args)

    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert isinstance(data, list)
    assert "Minion" in data
    assert "Tile" in data
    assert "Door" in data


def test_cmd_prefabs_json_counts(tmp_path: Path, capsys):
    """Should output prefab counts as JSON."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    import argparse

    args = argparse.Namespace(file=save_path, counts=True, json=True, allow_minor_mismatch=True)

    result = cmd_prefabs(args)

    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert isinstance(data, dict)
    assert data["Minion"] == 8
    assert data["Tile"] == 500
    assert data["Door"] == 20


def test_main_no_command(capsys):
    """Should show help when no command given."""
    with patch.object(sys, "argv", ["oni-save-parser"]):
        result = main()

    assert result == 1

    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_main_info_command(tmp_path: Path, capsys):
    """Should execute info command."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    with patch.object(sys, "argv", ["oni-save-parser", "info", str(save_path)]):
        result = main()

    assert result == 0

    captured = capsys.readouterr()
    assert "CLI Test Base" in captured.out


def test_main_prefabs_command(tmp_path: Path, capsys):
    """Should execute prefabs command."""
    save_path = tmp_path / "test.sav"
    create_test_save_file(save_path)

    with patch.object(sys, "argv", ["oni-save-parser", "prefabs", str(save_path)]):
        result = main()

    assert result == 0

    captured = capsys.readouterr()
    assert "Minion" in captured.out


def test_main_version(capsys):
    """Should show version."""
    with patch.object(sys, "argv", ["oni-save-parser", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "0.4.0" in captured.out


def test_main_help(capsys):
    """Should show help."""
    with patch.object(sys, "argv", ["oni-save-parser", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "Parse and analyze Oxygen Not Included save files" in captured.out


def test_cmd_prefabs_error_handling(tmp_path: Path, capsys):
    """Should handle errors gracefully."""
    import argparse

    args = argparse.Namespace(
        file=tmp_path / "nonexistent.sav",
        counts=False,
        json=False,
        allow_minor_mismatch=True,
    )

    result = cmd_prefabs(args)

    assert result == 1

    captured = capsys.readouterr()
    assert "Error:" in captured.err
