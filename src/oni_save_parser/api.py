"""High-level API for ONI save file parsing.

This module provides simple functions for loading and saving ONI save files.
"""

from pathlib import Path
from typing import Any

from oni_save_parser.save_structure import SaveGame, parse_save_game, unparse_save_game


def load_save_file(
    file_path: str | Path, verify_version: bool = True, allow_minor_mismatch: bool = True
) -> SaveGame:
    """Load an ONI save file from disk.

    Args:
        file_path: Path to the .sav file
        verify_version: Whether to verify save version compatibility
        allow_minor_mismatch: Allow different minor versions (default: True)

    Returns:
        Parsed SaveGame structure

    Raises:
        FileNotFoundError: If file doesn't exist
        VersionMismatchError: If save version is incompatible
        CorruptionError: If save data is corrupted

    Example:
        >>> from oni_save_parser import load_save_file
        >>> save = load_save_file("MyBase.sav")
        >>> print(f"Colony: {save.header.game_info.base_name}")
        >>> print(f"Cycle: {save.header.game_info.number_of_cycles}")
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Save file not found: {file_path}")

    data = path.read_bytes()
    return parse_save_game(
        data,
        verify_version=verify_version,
        allow_minor_mismatch=allow_minor_mismatch,
    )


def save_to_file(save_game: SaveGame, file_path: str | Path) -> None:
    """Write a SaveGame to disk.

    Args:
        save_game: SaveGame structure to write
        file_path: Output path for the .sav file

    Example:
        >>> from oni_save_parser import load_save_file, save_to_file
        >>> save = load_save_file("MyBase.sav")
        >>> # Modify save data here...
        >>> save_to_file(save, "MyBase_modified.sav")
    """
    path = Path(file_path)
    data = unparse_save_game(save_game)
    path.write_bytes(data)


def get_colony_info(save_game: SaveGame) -> dict[str, Any]:
    """Extract colony information from a save game.

    Args:
        save_game: Parsed SaveGame

    Returns:
        Dictionary with colony information

    Example:
        >>> from oni_save_parser import load_save_file, get_colony_info
        >>> save = load_save_file("MyBase.sav")
        >>> info = get_colony_info(save)
        >>> print(f"Colony: {info['colony_name']}")
        >>> print(f"Cycle: {info['cycle']}")
        >>> print(f"Duplicants: {info['duplicant_count']}")
    """
    info = save_game.header.game_info
    return {
        "colony_name": info.base_name,
        "cycle": info.number_of_cycles,
        "duplicant_count": info.number_of_duplicants,
        "cluster_id": info.cluster_id,
        "dlc_id": info.dlc_id,
        "is_auto_save": info.is_auto_save,
        "sandbox_enabled": info.sandbox_enabled,
        "save_version": f"{info.save_major_version}.{info.save_minor_version}",
        "build_version": save_game.header.build_version,
        "compressed": save_game.header.is_compressed,
    }


def get_game_objects_by_prefab(save_game: SaveGame, prefab_name: str) -> list[Any]:
    """Get all game objects with a specific prefab name.

    Args:
        save_game: Parsed SaveGame
        prefab_name: Prefab name to filter by (e.g., "Minion", "Tile", "Door")

    Returns:
        List of GameObjects matching the prefab name

    Example:
        >>> from oni_save_parser import load_save_file, get_game_objects_by_prefab
        >>> save = load_save_file("MyBase.sav")
        >>> minions = get_game_objects_by_prefab(save, "Minion")
        >>> print(f"Found {len(minions)} duplicants")
        >>> for minion in minions:
        ...     print(f"Position: {minion.position}")
    """
    for group in save_game.game_objects:
        if group.prefab_name == prefab_name:
            return group.objects
    return []


def list_prefab_types(save_game: SaveGame) -> list[str]:
    """List all prefab types present in the save file.

    Args:
        save_game: Parsed SaveGame

    Returns:
        List of unique prefab names

    Example:
        >>> from oni_save_parser import load_save_file, list_prefab_types
        >>> save = load_save_file("MyBase.sav")
        >>> prefabs = list_prefab_types(save)
        >>> print(f"Found {len(prefabs)} prefab types")
        >>> for prefab in sorted(prefabs):
        ...     print(prefab)
    """
    return [group.prefab_name for group in save_game.game_objects]


def get_prefab_counts(save_game: SaveGame) -> dict[str, int]:
    """Get count of game objects for each prefab type.

    Args:
        save_game: Parsed SaveGame

    Returns:
        Dictionary mapping prefab names to counts

    Example:
        >>> from oni_save_parser import load_save_file, get_prefab_counts
        >>> save = load_save_file("MyBase.sav")
        >>> counts = get_prefab_counts(save)
        >>> print(f"Duplicants: {counts.get('Minion', 0)}")
        >>> print(f"Doors: {counts.get('Door', 0)}")
    """
    return {group.prefab_name: len(group.objects) for group in save_game.game_objects}
