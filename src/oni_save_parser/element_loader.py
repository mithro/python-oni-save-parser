"""Load and cache element properties from ONI game data files."""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ElementLoader:
    """Loads element data from ONI YAML files."""

    def __init__(self, elements_path: Path) -> None:
        """Initialize element loader.

        Args:
            elements_path: Path to ONI StreamingAssets/elements directory
        """
        self._elements_path = elements_path
        self._elements_cache: dict[str, dict[str, Any]] = {}
        self._load_elements()

    def _load_elements(self) -> None:
        """Load all element data from YAML files."""
        files_loaded = 0

        for filename in ["gas.yaml", "liquid.yaml"]:
            filepath = self._elements_path / filename
            if filepath.exists():
                try:
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                        if data and "elements" in data:
                            for element in data["elements"]:
                                element_id = element.get("elementId")
                                if element_id:
                                    self._elements_cache[element_id] = {
                                        "element_id": element_id,
                                        "state": element.get("state"),
                                        "specific_heat_capacity": element.get("specificHeatCapacity"),
                                        "max_mass": element.get("maxMass"),
                                    }
                    files_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")

        if files_loaded == 0:
            logger.warning(
                f"Element data files not found at {self._elements_path}. "
                "Thermal calculations will be unavailable."
            )

    def get_element(self, element_id: str) -> dict[str, Any] | None:
        """Get element properties by ID.

        Args:
            element_id: Element ID (e.g., "Steam", "Water")

        Returns:
            Element properties dictionary or None if not found
        """
        return self._elements_cache.get(element_id)


def find_elements_path() -> Path | None:
    """Find ONI elements directory automatically.

    Searches common Steam installation locations.

    Returns:
        Path to elements directory or None if not found
    """
    search_paths = [
        Path.home()
        / ".local/share/Steam/steamapps/common/OxygenNotIncluded"
        / "OxygenNotIncluded_Data/StreamingAssets/elements",
        Path.home()
        / ".steam/steam/steamapps/common/OxygenNotIncluded"
        / "OxygenNotIncluded_Data/StreamingAssets/elements",
    ]

    # Check environment variable
    if "ONI_INSTALL_PATH" in os.environ:
        custom_path = (
            Path(os.environ["ONI_INSTALL_PATH"])
            / "OxygenNotIncluded_Data/StreamingAssets/elements"
        )
        search_paths.insert(0, custom_path)

    for path in search_paths:
        if path.exists() and (path / "gas.yaml").exists():
            return path

    return None


def get_global_element_loader() -> ElementLoader | None:
    """Get a global ElementLoader instance with auto-discovered path.

    Returns:
        ElementLoader instance or None if elements path not found
    """
    elements_path = find_elements_path()
    if elements_path:
        return ElementLoader(elements_path)
    return None
