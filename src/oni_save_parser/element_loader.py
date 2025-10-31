"""Load and cache element properties from ONI game data files."""

from pathlib import Path
from typing import Any

import yaml


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
        for filename in ["gas.yaml", "liquid.yaml"]:
            filepath = self._elements_path / filename
            if filepath.exists():
                with open(filepath) as f:
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

    def get_element(self, element_id: str) -> dict[str, Any] | None:
        """Get element properties by ID.

        Args:
            element_id: Element ID (e.g., "Steam", "Water")

        Returns:
            Element properties dictionary or None if not found
        """
        return self._elements_cache.get(element_id)
