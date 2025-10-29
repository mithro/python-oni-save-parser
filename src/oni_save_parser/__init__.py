"""ONI Save Parser - Parse Oxygen Not Included save files."""

from .api import (
    get_colony_info,
    get_game_objects_by_prefab,
    get_prefab_counts,
    list_prefab_types,
    load_save_file,
    save_to_file,
)
from .save_structure import SaveGame
from .utils import get_sdbm32_lower_hash

__version__ = "0.4.0"

__all__ = [
    # High-level API
    "load_save_file",
    "save_to_file",
    "get_colony_info",
    "get_game_objects_by_prefab",
    "list_prefab_types",
    "get_prefab_counts",
    # Core types
    "SaveGame",
    # Utilities
    "get_sdbm32_lower_hash",
]
