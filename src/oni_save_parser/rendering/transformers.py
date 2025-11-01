"""Data transformer for converting save data to WorldModel."""
from typing import Any

from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.models import (
    AsteroidData,
    Cell,
    ElementState,
    SaveMetadata,
    WorldModel,
)


class DataTransformer:
    """Transforms parsed save data into WorldModel."""

    def __init__(self, element_registry: ElementRegistry) -> None:
        """
        Initialize transformer.

        Args:
            element_registry: Registry for element lookups
        """
        self.element_registry = element_registry

    def transform(self, save_data: Any) -> WorldModel:
        """
        Transform save data to WorldModel.

        Args:
            save_data: Parsed save file data

        Returns:
            WorldModel ready for rendering
        """
        # Extract metadata
        metadata = self._extract_metadata(save_data)

        # Extract asteroids (Phase 1: just handle first world)
        asteroids = self._extract_asteroids(save_data)

        return WorldModel(asteroids=asteroids, metadata=metadata)

    def _extract_metadata(self, save_data: Any) -> SaveMetadata:
        """Extract metadata from save data."""
        # Get from header
        header = save_data.header
        info = header.game_info

        return SaveMetadata(
            colony_name=info.base_name,
            cycle_number=info.number_of_cycles,
            seed=info.cluster_id,
        )

    def _extract_asteroids(self, save_data: Any) -> list[AsteroidData]:
        """Extract asteroid data from save."""
        # Phase 1: Extract just the first world's grid
        # Future: Handle multi-asteroid DLC saves

        asteroids = []

        # Extract grid dimensions and cells
        width, height, cells = self._extract_grid(save_data)

        asteroid = AsteroidData(
            id="0",
            name="Main",  # Phase 1: placeholder name
            width=width,
            height=height,
            cells=cells,
        )

        asteroids.append(asteroid)
        return asteroids

    def _extract_grid(self, save_data: Any) -> tuple[int, int, list[list[Cell]]]:
        """
        Extract grid dimensions and cell data.

        Returns:
            (width, height, cells) where cells is 2D array cells[y][x]
        """
        # Get world bounds from world dict
        width = save_data.world.get("WidthInCells", 256)
        height = save_data.world.get("HeightInCells", 384)

        # Phase 1: Parse sim_data binary blob to extract grid data
        # sim_data contains element hashes, temperatures, masses, etc.
        element_hashes, temperatures, masses = self._parse_sim_data(save_data.sim_data, width, height)

        # Build 2D grid
        cells: list[list[Cell]] = []

        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                idx = y * width + x

                if idx < len(element_hashes):
                    # Get element name
                    element_hash = element_hashes[idx]
                    element = self._hash_to_element(element_hash)

                    # Get temperature
                    temp = temperatures[idx] if idx < len(temperatures) else 0.0

                    # Get mass
                    mass = masses[idx] if idx < len(masses) else 0.0

                    # Determine state from mass/element
                    state = self._determine_state(element, mass)

                    cell = Cell(element, state, temp, mass)
                else:
                    # Out of bounds - vacuum
                    cell = Cell("Vacuum", ElementState.GAS, 0.0, 0.0)

                row.append(cell)
            cells.append(row)

        return width, height, cells

    def _parse_sim_data(
        self, sim_data: bytes, width: int, height: int
    ) -> tuple[list[int], list[float], list[float]]:
        """
        Parse sim_data binary blob to extract grid data.

        Phase 1: Minimal parser that extracts elements, temperatures, and masses.
        Future: Complete sim_data parser.

        Returns:
            (element_hashes, temperatures, masses) as flattened arrays
        """
        from oni_save_parser.parser.parse import BinaryParser

        parser = BinaryParser(sim_data)

        # Verify SIMSAVE header
        header = parser.read_chars(7)
        if header != "SIMSAVE":
            # Return empty data if not parseable
            cell_count = width * height
            return ([0] * cell_count, [0.0] * cell_count, [0.0] * cell_count)

        # Skip version info (Phase 1: don't parse fully)
        parser.read_byte()  # version
        parser.read_int32()  # some count
        parser.read_int32()  # some value

        # The structure after header varies, but typically has:
        # - Grid dimensions (should match width/height)
        # - Element data array
        # - Temperature array
        # - Mass array
        # Phase 1: Create placeholder data
        cell_count = width * height

        # For now, return placeholder data
        # TODO: Implement full sim_data parser in future phase
        element_hashes = [0] * cell_count  # All vacuum
        temperatures = [293.15] * cell_count  # Room temperature
        masses = [0.0] * cell_count  # No mass (vacuum)

        return (element_hashes, temperatures, masses)

    def _hash_to_element(self, element_hash: int) -> str:
        """
        Convert element hash to element name.

        Phase 1: Return common element names for known hashes.
        Future: Load actual hash->name mapping.
        """
        # Common element hashes (discovered empirically)
        known_hashes = {
            0: "Vacuum",
            1: "Granite",
            2: "SandStone",
            3: "Oxygen",
            4: "CarbonDioxide",
            5: "Water",
            6: "Dirt",
            7: "Sand",
        }

        return known_hashes.get(element_hash, f"Element_{element_hash}")

    def _determine_state(self, element: str, mass: float) -> ElementState:
        """
        Determine element state based on name and mass.

        Phase 1: Simple heuristics.
        Future: Load from game data.
        """
        if mass == 0.0:
            return ElementState.GAS

        # Gas elements
        if element in ("Oxygen", "CarbonDioxide", "Hydrogen", "ChlorineGas", "Steam", "Vacuum"):
            return ElementState.GAS

        # Liquid elements
        if element in ("Water", "DirtyWater", "SaltWater", "Brine", "CrudeOil", "Petroleum"):
            return ElementState.LIQUID

        # Everything else is solid
        return ElementState.SOLID
