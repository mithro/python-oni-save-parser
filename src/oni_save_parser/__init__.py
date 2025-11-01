"""ONI Save Parser - Parse Oxygen Not Included save files."""

from .api import (
    get_colony_info,
    get_game_objects_by_prefab,
    get_prefab_counts,
    list_prefab_types,
    load_save_file,
    save_to_file,
)
from .element_loader import ElementLoader, find_elements_path, get_global_element_loader
from .save_structure import SaveGame
from .utils import get_sdbm32_lower_hash

__version__ = "1.0.0"

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
    # Element loader
    "ElementLoader",
    "find_elements_path",
    "get_global_element_loader",
    # Utilities
    "get_sdbm32_lower_hash",
]
