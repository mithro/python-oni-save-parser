# Map Rendering Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Phase 1 MVP - render terrain-only maps from ONI save files to PNG images

**Architecture:** Pipeline-based system with 4 stages (Parse → Transform → Layout → Render). Phase 1 focuses on single-asteroid terrain rendering with fallback colors, no game asset extraction yet.

**Tech Stack:** Python 3.12+, Pillow (PIL) for image rendering, existing oni_save_parser for save file parsing

---

## Task 1: Fallback Color Palette

**Files:**
- Create: `src/oni_save_parser/assets/__init__.py`
- Create: `src/oni_save_parser/assets/fallback_colors.py`
- Create: `tests/rendering/__init__.py`
- Create: `tests/rendering/test_fallback_colors.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_fallback_colors.py`:

```python
"""Tests for fallback color palette."""
from oni_save_parser.assets.fallback_colors import FALLBACK_COLORS, get_fallback_color


def test_fallback_colors_contains_common_elements() -> None:
    """Test that fallback colors include common ONI elements."""
    assert "Oxygen" in FALLBACK_COLORS
    assert "Granite" in FALLBACK_COLORS
    assert "Water" in FALLBACK_COLORS
    assert "Sand" in FALLBACK_COLORS


def test_fallback_colors_are_rgb_tuples() -> None:
    """Test that all colors are valid RGB tuples."""
    for element, color in FALLBACK_COLORS.items():
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)
        assert all(0 <= c <= 255 for c in color)


def test_get_fallback_color_known_element() -> None:
    """Test getting color for known element."""
    color = get_fallback_color("Oxygen")
    assert color == FALLBACK_COLORS["Oxygen"]


def test_get_fallback_color_unknown_element() -> None:
    """Test getting color for unknown element returns magenta."""
    color = get_fallback_color("UnknownElement123")
    assert color == (255, 0, 255)  # Magenta
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_fallback_colors.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.assets'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/assets/__init__.py`:

```python
"""Asset loading and management for ONI save file rendering."""
```

Create `src/oni_save_parser/assets/fallback_colors.py`:

```python
"""Fallback color palette for ONI elements when game assets unavailable."""

# RGB color tuples for common ONI elements
FALLBACK_COLORS: dict[str, tuple[int, int, int]] = {
    # Gases
    "Oxygen": (161, 219, 251),
    "CarbonDioxide": (88, 88, 88),
    "Hydrogen": (249, 226, 226),
    "ChlorineGas": (205, 255, 155),
    "Steam": (220, 220, 220),

    # Liquids
    "Water": (44, 111, 209),
    "DirtyWater": (115, 103, 82),
    "SaltWater": (93, 151, 185),
    "Brine": (162, 130, 101),
    "CrudeOil": (67, 47, 45),
    "Petroleum": (50, 39, 40),

    # Solids - Basic
    "Vacuum": (0, 0, 0),
    "Dirt": (115, 86, 58),
    "Sand": (192, 167, 106),
    "Clay": (146, 108, 82),
    "Granite": (124, 124, 124),
    "SandStone": (145, 117, 69),
    "Algae": (87, 152, 50),
    "Ice": (175, 218, 245),

    # Solids - Metals
    "IronOre": (170, 98, 65),
    "Copper": (184, 115, 51),
    "GoldAmalgam": (237, 201, 81),
    "Wolframite": (71, 71, 71),

    # Solids - Special
    "Phosphorite": (253, 222, 108),
    "Coal": (39, 39, 39),
    "Fertilizer": (158, 135, 98),
    "BleachStone": (255, 215, 180),
}

# Magenta for unknown elements (highly visible)
UNKNOWN_COLOR: tuple[int, int, int] = (255, 0, 255)


def get_fallback_color(element: str) -> tuple[int, int, int]:
    """
    Get fallback color for an element.

    Args:
        element: Element name/ID

    Returns:
        RGB color tuple (r, g, b) where each component is 0-255
    """
    return FALLBACK_COLORS.get(element, UNKNOWN_COLOR)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_fallback_colors.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/oni_save_parser/assets/ tests/rendering/
git commit -m "feat(rendering): add fallback color palette for elements"
```

---

## Task 2: ElementRegistry

**Files:**
- Create: `src/oni_save_parser/assets/element_registry.py`
- Create: `tests/rendering/test_element_registry.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_element_registry.py`:

```python
"""Tests for ElementRegistry."""
from oni_save_parser.assets.element_registry import ElementRegistry


def test_element_registry_initialization() -> None:
    """Test creating an ElementRegistry."""
    registry = ElementRegistry()
    assert registry is not None


def test_element_registry_get_known_color() -> None:
    """Test getting color for known element."""
    registry = ElementRegistry()
    color = registry.get_color("Oxygen")
    assert isinstance(color, tuple)
    assert len(color) == 3
    assert all(0 <= c <= 255 for c in color)


def test_element_registry_get_unknown_color() -> None:
    """Test getting color for unknown element returns magenta."""
    registry = ElementRegistry()
    color = registry.get_color("UnknownElement999")
    assert color == (255, 0, 255)  # Magenta


def test_element_registry_consistency() -> None:
    """Test that same element returns same color."""
    registry = ElementRegistry()
    color1 = registry.get_color("Water")
    color2 = registry.get_color("Water")
    assert color1 == color2
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_element_registry.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.assets.element_registry'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/assets/element_registry.py`:

```python
"""Element registry for mapping element IDs to visual properties."""
from oni_save_parser.assets.fallback_colors import get_fallback_color


class ElementRegistry:
    """
    Maps element IDs to colors.

    Phase 1: Uses only fallback colors.
    Future: Load from game assets when available.
    """

    def __init__(self) -> None:
        """Initialize the registry with fallback colors."""
        # Future: Accept optional GameAssetLoader
        pass

    def get_color(self, element: str) -> tuple[int, int, int]:
        """
        Get RGB color for an element.

        Args:
            element: Element name/ID

        Returns:
            RGB tuple (r, g, b) where each component is 0-255
        """
        return get_fallback_color(element)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_element_registry.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/oni_save_parser/assets/element_registry.py tests/rendering/test_element_registry.py
git commit -m "feat(rendering): add ElementRegistry for color mapping"
```

---

## Task 3: WorldModel Data Structures

**Files:**
- Create: `src/oni_save_parser/rendering/__init__.py`
- Create: `src/oni_save_parser/rendering/models.py`
- Create: `tests/rendering/test_models.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_models.py`:

```python
"""Tests for rendering data models."""
from oni_save_parser.rendering.models import (
    Cell,
    ElementState,
    AsteroidData,
    SaveMetadata,
    WorldModel,
)


def test_cell_creation() -> None:
    """Test creating a Cell."""
    cell = Cell(
        element="Oxygen",
        state=ElementState.GAS,
        temperature=300.0,
        mass=1.0,
    )
    assert cell.element == "Oxygen"
    assert cell.state == ElementState.GAS
    assert cell.temperature == 300.0
    assert cell.mass == 1.0


def test_element_state_enum() -> None:
    """Test ElementState enum values."""
    assert ElementState.SOLID.value == "solid"
    assert ElementState.LIQUID.value == "liquid"
    assert ElementState.GAS.value == "gas"


def test_asteroid_data_creation() -> None:
    """Test creating AsteroidData."""
    cells = [[Cell("Vacuum", ElementState.GAS, 0.0, 0.0) for _ in range(10)] for _ in range(10)]
    asteroid = AsteroidData(
        id="1",
        name="Terra",
        width=10,
        height=10,
        cells=cells,
    )
    assert asteroid.id == "1"
    assert asteroid.name == "Terra"
    assert asteroid.width == 10
    assert asteroid.height == 10
    assert len(asteroid.cells) == 10
    assert len(asteroid.cells[0]) == 10


def test_save_metadata_creation() -> None:
    """Test creating SaveMetadata."""
    metadata = SaveMetadata(
        colony_name="TestColony",
        cycle_number=100,
        seed="12345",
    )
    assert metadata.colony_name == "TestColony"
    assert metadata.cycle_number == 100
    assert metadata.seed == "12345"


def test_world_model_creation() -> None:
    """Test creating WorldModel."""
    metadata = SaveMetadata("Colony", 50, "seed")
    cells = [[Cell("Dirt", ElementState.SOLID, 298.0, 1000.0)]]
    asteroid = AsteroidData("1", "Terra", 1, 1, cells)

    model = WorldModel(
        asteroids=[asteroid],
        metadata=metadata,
    )
    assert len(model.asteroids) == 1
    assert model.metadata.colony_name == "Colony"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_models.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.rendering'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/rendering/__init__.py`:

```python
"""Rendering system for ONI save files."""
```

Create `src/oni_save_parser/rendering/models.py`:

```python
"""Data models for rendering pipeline."""
from dataclasses import dataclass
from enum import Enum


class ElementState(Enum):
    """Physical state of an element."""
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"


@dataclass
class Cell:
    """Single grid cell in the world."""
    element: str
    state: ElementState
    temperature: float
    mass: float


@dataclass
class AsteroidData:
    """Data for a single asteroid/world."""
    id: str
    name: str
    width: int
    height: int
    cells: list[list[Cell]]  # 2D grid: cells[y][x]


@dataclass
class SaveMetadata:
    """Metadata about the save file."""
    colony_name: str
    cycle_number: int
    seed: str


@dataclass
class WorldModel:
    """Complete world model for rendering."""
    asteroids: list[AsteroidData]
    metadata: SaveMetadata
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_models.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/oni_save_parser/rendering/ tests/rendering/test_models.py
git commit -m "feat(rendering): add WorldModel data structures"
```

---

## Task 4: Add Pillow Dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add Pillow to dependencies**

Edit `pyproject.toml`, find the `dependencies` line and update:

```toml
dependencies = ["pyyaml>=6.0", "pillow>=10.0.0"]
```

**Step 2: Sync dependencies**

Run: `uv sync`

Expected: Pillow installed successfully

**Step 3: Verify Pillow available**

Run: `uv run python -c "from PIL import Image; print('Pillow OK')"`

Expected: Output "Pillow OK"

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: add Pillow dependency for image rendering"
```

---

## Task 5: CellRenderer

**Files:**
- Create: `src/oni_save_parser/rendering/cell_renderer.py`
- Create: `tests/rendering/test_cell_renderer.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_cell_renderer.py`:

```python
"""Tests for CellRenderer."""
from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.cell_renderer import CellRenderer
from oni_save_parser.rendering.models import Cell, ElementState


def test_cell_renderer_initialization() -> None:
    """Test creating a CellRenderer."""
    registry = ElementRegistry()
    renderer = CellRenderer(registry)
    assert renderer is not None


def test_render_solid_cell() -> None:
    """Test rendering a solid element cell."""
    registry = ElementRegistry()
    renderer = CellRenderer(registry)

    cell = Cell("Granite", ElementState.SOLID, 298.0, 1000.0)
    color = renderer.render_cell(cell)

    assert isinstance(color, tuple)
    assert len(color) == 3
    assert all(isinstance(c, int) for c in color)
    assert all(0 <= c <= 255 for c in color)


def test_render_liquid_cell() -> None:
    """Test rendering a liquid element cell."""
    registry = ElementRegistry()
    renderer = CellRenderer(registry)

    cell = Cell("Water", ElementState.LIQUID, 298.0, 1000.0)
    color = renderer.render_cell(cell)

    # Should be a valid color (liquid effect applied)
    assert isinstance(color, tuple)
    assert len(color) == 3


def test_render_gas_cell() -> None:
    """Test rendering a gas element cell."""
    registry = ElementRegistry()
    renderer = CellRenderer(registry)

    cell = Cell("Oxygen", ElementState.GAS, 298.0, 1.0)
    color = renderer.render_cell(cell)

    # Should be a valid color (gas effect applied)
    assert isinstance(color, tuple)
    assert len(color) == 3


def test_render_vacuum_cell() -> None:
    """Test rendering vacuum (empty) cell."""
    registry = ElementRegistry()
    renderer = CellRenderer(registry)

    cell = Cell("Vacuum", ElementState.GAS, 0.0, 0.0)
    color = renderer.render_cell(cell)

    # Vacuum should be black
    assert color == (0, 0, 0)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_cell_renderer.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.rendering.cell_renderer'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/rendering/cell_renderer.py`:

```python
"""Cell renderer for converting cells to colors."""
from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.models import Cell, ElementState


class CellRenderer:
    """Renders individual cells to RGB colors."""

    def __init__(self, element_registry: ElementRegistry) -> None:
        """
        Initialize renderer.

        Args:
            element_registry: Registry for element colors
        """
        self.element_registry = element_registry

    def render_cell(self, cell: Cell) -> tuple[int, int, int]:
        """
        Render a cell to an RGB color.

        Args:
            cell: Cell to render

        Returns:
            RGB color tuple (r, g, b)
        """
        # Get base color from registry
        color = self.element_registry.get_color(cell.element)

        # Apply state-based visual effects
        if cell.state == ElementState.LIQUID:
            return self._apply_liquid_effect(color)
        elif cell.state == ElementState.GAS:
            return self._apply_gas_effect(color)
        else:  # SOLID
            return color

    def _apply_liquid_effect(self, color: tuple[int, int, int]) -> tuple[int, int, int]:
        """
        Apply visual effect for liquids (slight brightness boost).

        Args:
            color: Base RGB color

        Returns:
            Modified RGB color
        """
        r, g, b = color
        # Increase brightness by 10%
        factor = 1.1
        return (
            min(255, int(r * factor)),
            min(255, int(g * factor)),
            min(255, int(b * factor)),
        )

    def _apply_gas_effect(self, color: tuple[int, int, int]) -> tuple[int, int, int]:
        """
        Apply visual effect for gases (lighter appearance).

        Args:
            color: Base RGB color

        Returns:
            Modified RGB color
        """
        r, g, b = color
        # Lighten by blending with white (60% original, 40% white)
        factor = 0.6
        return (
            int(r * factor + 255 * (1 - factor)),
            int(g * factor + 255 * (1 - factor)),
            int(b * factor + 255 * (1 - factor)),
        )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_cell_renderer.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/oni_save_parser/rendering/cell_renderer.py tests/rendering/test_cell_renderer.py
git commit -m "feat(rendering): add CellRenderer for cell-to-color conversion"
```

---

## Task 6: DataTransformer (Minimal)

**Files:**
- Create: `src/oni_save_parser/rendering/transformers.py`
- Create: `tests/rendering/test_transformers.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_transformers.py`:

```python
"""Tests for DataTransformer."""
import tempfile
from pathlib import Path

from oni_save_parser import load_save_file
from oni_save_parser.rendering.transformers import DataTransformer
from oni_save_parser.assets.element_registry import ElementRegistry


def test_data_transformer_initialization() -> None:
    """Test creating a DataTransformer."""
    registry = ElementRegistry()
    transformer = DataTransformer(registry)
    assert transformer is not None


def test_transform_with_real_save(tmp_path: Path) -> None:
    """Test transforming a real save file to WorldModel."""
    # Use existing test save
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        # Skip if test save not available
        import pytest
        pytest.skip("Test save file not available")

    # Load and transform
    registry = ElementRegistry()
    transformer = DataTransformer(registry)
    save_data = load_save_file(save_path)

    world_model = transformer.transform(save_data)

    # Verify basic structure
    assert world_model is not None
    assert world_model.metadata is not None
    assert len(world_model.asteroids) > 0

    # Verify first asteroid has data
    asteroid = world_model.asteroids[0]
    assert asteroid.width > 0
    assert asteroid.height > 0
    assert len(asteroid.cells) == asteroid.height
    assert len(asteroid.cells[0]) == asteroid.width
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_transformers.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.rendering.transformers'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/rendering/transformers.py`:

```python
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
            colony_name=info.get("baseName", "Unknown"),
            cycle_number=info.get("numberOfCycles", 0),
            seed=info.get("worldID", "unknown"),
        )

    def _extract_asteroids(self, save_data: Any) -> list[AsteroidData]:
        """Extract asteroid data from save."""
        # Phase 1: Extract just the first world's grid
        # Future: Handle multi-asteroid DLC saves

        asteroids = []

        # Get world data from save
        world_data = save_data.world_data

        # Extract grid dimensions and cells
        # Note: ONI saves store grid data in sim_data.elementHashes and sim_data.elements
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
        # Access sim_data which contains the grid
        sim_data = save_data.world_data.get("simData", {})

        # Get world bounds
        world_bounds = sim_data.get("world", {}).get("data", {})
        width = world_bounds.get("x", 256)  # Default ONI world size
        height = world_bounds.get("y", 384)

        # Get element data (flattened array)
        # elementHashes contains element IDs as integers
        element_hashes = sim_data.get("elementHashes", [])

        # Temperature and mass data
        temperatures = sim_data.get("temperature", [])
        masses = sim_data.get("mass", [])

        # Build 2D grid
        cells: list[list[Cell]] = []

        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                idx = y * width + x

                if idx < len(element_hashes):
                    # Get element name (Phase 1: use hash as string)
                    # Future: Map hash to element name
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_transformers.py -v`

Expected: PASS (or SKIP if test save not available)

**Step 5: Commit**

```bash
git add src/oni_save_parser/rendering/transformers.py tests/rendering/test_transformers.py
git commit -m "feat(rendering): add DataTransformer for save->WorldModel conversion"
```

---

## Task 7: StaticRenderer

**Files:**
- Create: `src/oni_save_parser/rendering/static_renderer.py`
- Create: `tests/rendering/test_static_renderer.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_static_renderer.py`:

```python
"""Tests for StaticRenderer."""
from pathlib import Path

from PIL import Image

from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.cell_renderer import CellRenderer
from oni_save_parser.rendering.models import (
    AsteroidData,
    Cell,
    ElementState,
    SaveMetadata,
    WorldModel,
)
from oni_save_parser.rendering.static_renderer import StaticRenderer


def test_static_renderer_initialization() -> None:
    """Test creating a StaticRenderer."""
    registry = ElementRegistry()
    renderer = StaticRenderer(registry, scale=2)
    assert renderer is not None


def test_render_simple_asteroid(tmp_path: Path) -> None:
    """Test rendering a simple 3x3 asteroid."""
    # Create simple test world
    cells = [
        [
            Cell("Granite", ElementState.SOLID, 298.0, 1000.0),
            Cell("Oxygen", ElementState.GAS, 298.0, 1.0),
            Cell("Water", ElementState.LIQUID, 298.0, 1000.0),
        ],
        [
            Cell("Dirt", ElementState.SOLID, 298.0, 1000.0),
            Cell("Sand", ElementState.SOLID, 298.0, 1000.0),
            Cell("Vacuum", ElementState.GAS, 0.0, 0.0),
        ],
        [
            Cell("Ice", ElementState.SOLID, 250.0, 1000.0),
            Cell("CarbonDioxide", ElementState.GAS, 298.0, 1.0),
            Cell("Granite", ElementState.SOLID, 298.0, 1000.0),
        ],
    ]

    asteroid = AsteroidData(
        id="test",
        name="TestWorld",
        width=3,
        height=3,
        cells=cells,
    )

    metadata = SaveMetadata("TestColony", 1, "seed123")
    world_model = WorldModel([asteroid], metadata)

    # Render
    output_path = tmp_path / "test_output.png"
    registry = ElementRegistry()
    renderer = StaticRenderer(registry, scale=2)

    renderer.render_asteroid(asteroid, output_path)

    # Verify file created
    assert output_path.exists()

    # Verify it's a valid image
    img = Image.open(output_path)
    assert img.size == (6, 6)  # 3x3 at scale=2
    assert img.mode == "RGB"


def test_render_respects_scale(tmp_path: Path) -> None:
    """Test that scale parameter affects output size."""
    cells = [[Cell("Dirt", ElementState.SOLID, 298.0, 1000.0) for _ in range(5)] for _ in range(5)]
    asteroid = AsteroidData("test", "Test", 5, 5, cells)

    output_path = tmp_path / "scaled.png"
    registry = ElementRegistry()

    # Test scale=4
    renderer = StaticRenderer(registry, scale=4)
    renderer.render_asteroid(asteroid, output_path)

    img = Image.open(output_path)
    assert img.size == (20, 20)  # 5x5 at scale=4
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_static_renderer.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.rendering.static_renderer'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/rendering/static_renderer.py`:

```python
"""Static PNG renderer for ONI save files."""
from pathlib import Path

from PIL import Image

from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.cell_renderer import CellRenderer
from oni_save_parser.rendering.models import AsteroidData


class StaticRenderer:
    """Renders asteroids to static PNG images."""

    def __init__(self, element_registry: ElementRegistry, scale: int = 2) -> None:
        """
        Initialize renderer.

        Args:
            element_registry: Registry for element colors
            scale: Pixels per tile (1-10)
        """
        self.element_registry = element_registry
        self.scale = max(1, min(10, scale))  # Clamp to 1-10
        self.cell_renderer = CellRenderer(element_registry)

    def render_asteroid(
        self,
        asteroid: AsteroidData,
        output_path: Path | str,
    ) -> None:
        """
        Render an asteroid to a PNG file.

        Args:
            asteroid: Asteroid data to render
            output_path: Output file path
        """
        # Calculate output dimensions
        width = asteroid.width * self.scale
        height = asteroid.height * self.scale

        # Create image
        img = Image.new("RGB", (width, height))
        pixels = img.load()

        # Render each cell
        for y in range(asteroid.height):
            for x in range(asteroid.width):
                cell = asteroid.cells[y][x]
                color = self.cell_renderer.render_cell(cell)

                # Fill scaled tile
                for dy in range(self.scale):
                    for dx in range(self.scale):
                        px = x * self.scale + dx
                        py = y * self.scale + dy
                        pixels[px, py] = color

        # Save image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_static_renderer.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/oni_save_parser/rendering/static_renderer.py tests/rendering/test_static_renderer.py
git commit -m "feat(rendering): add StaticRenderer for PNG output"
```

---

## Task 8: Pipeline Orchestrator

**Files:**
- Create: `src/oni_save_parser/rendering/pipeline.py`
- Create: `tests/rendering/test_pipeline.py`

**Step 1: Write the failing test**

Create `tests/rendering/test_pipeline.py`:

```python
"""Tests for pipeline orchestrator."""
from pathlib import Path

from oni_save_parser.rendering.pipeline import MapRenderer


def test_map_renderer_initialization() -> None:
    """Test creating a MapRenderer."""
    renderer = MapRenderer()
    assert renderer is not None


def test_render_save_to_png(tmp_path: Path) -> None:
    """Test end-to-end rendering of a save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        import pytest
        pytest.skip("Test save file not available")

    output_dir = tmp_path / "renders"
    renderer = MapRenderer()

    output_files = renderer.render(
        save_path=save_path,
        output_dir=output_dir,
        scale=2,
    )

    # Verify output files created
    assert len(output_files) > 0
    for file_path in output_files:
        assert Path(file_path).exists()
        assert Path(file_path).suffix == ".png"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/rendering/test_pipeline.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.rendering.pipeline'"

**Step 3: Write minimal implementation**

Create `src/oni_save_parser/rendering/pipeline.py`:

```python
"""Pipeline orchestrator for map rendering."""
from pathlib import Path

from oni_save_parser import load_save_file
from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.static_renderer import StaticRenderer
from oni_save_parser.rendering.transformers import DataTransformer


class MapRenderer:
    """Orchestrates the map rendering pipeline."""

    def __init__(self) -> None:
        """Initialize the renderer pipeline."""
        # Phase 1: No game assets, use fallback colors only
        self.element_registry = ElementRegistry()
        self.transformer = DataTransformer(self.element_registry)

    def render(
        self,
        save_path: Path | str,
        output_dir: Path | str,
        scale: int = 2,
    ) -> list[str]:
        """
        Render all asteroids from a save file to PNG images.

        Args:
            save_path: Path to .sav file
            output_dir: Directory for output PNG files
            scale: Pixels per tile (1-10)

        Returns:
            List of output file paths created
        """
        save_path = Path(save_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Parse
        save_data = load_save_file(save_path)

        # Stage 2: Transform
        world_model = self.transformer.transform(save_data)

        # Stage 3: Render each asteroid
        renderer = StaticRenderer(self.element_registry, scale=scale)
        output_files = []

        for asteroid in world_model.asteroids:
            # Build output filename
            output_path = self._build_output_path(
                output_dir,
                world_model.metadata,
                asteroid,
            )

            # Render
            renderer.render_asteroid(asteroid, output_path)
            output_files.append(str(output_path))

        return output_files

    def _build_output_path(
        self,
        output_dir: Path,
        metadata: Any,
        asteroid: Any,
    ) -> Path:
        """Build output filename for an asteroid."""
        # Sanitize colony name
        colony_name = metadata.colony_name.replace(" ", "-")

        filename = (
            f"{colony_name}_"
            f"cycle-{metadata.cycle_number}_"
            f"asteroid-{asteroid.id}-{asteroid.name}.png"
        )

        return output_dir / filename
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/rendering/test_pipeline.py -v`

Expected: PASS (or SKIP if test save not available)

**Step 5: Commit**

```bash
git add src/oni_save_parser/rendering/pipeline.py tests/rendering/test_pipeline.py
git commit -m "feat(rendering): add MapRenderer pipeline orchestrator"
```

---

## Task 9: CLI Tool

**Files:**
- Create: `examples/render_map.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_render_map_cli.py`

**Step 1: Write the failing test**

Create `tests/integration/test_render_map_cli.py`:

```python
"""Integration tests for render_map CLI."""
import subprocess
from pathlib import Path


def test_render_map_help() -> None:
    """Test render_map --help."""
    result = subprocess.run(
        ["uv", "run", "python", "examples/render_map.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "render_map.py" in result.stdout
    assert "--output-dir" in result.stdout


def test_render_map_basic(tmp_path: Path) -> None:
    """Test basic rendering of a save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        import pytest
        pytest.skip("Test save file not available")

    output_dir = tmp_path / "renders"

    result = subprocess.run(
        [
            "uv", "run", "python", "examples/render_map.py",
            str(save_path),
            "--output-dir", str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_dir.exists()

    # Check that PNG files were created
    png_files = list(output_dir.glob("*.png"))
    assert len(png_files) > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/integration/test_render_map_cli.py -v`

Expected: FAIL with FileNotFoundError for examples/render_map.py

**Step 3: Write minimal implementation**

Create `examples/render_map.py`:

```python
#!/usr/bin/env python3
"""CLI tool for rendering ONI save files to images."""
import argparse
from pathlib import Path

from oni_save_parser.rendering.pipeline import MapRenderer


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Render ONI save files to PNG images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render all asteroids from a save
  %(prog)s save.sav --output-dir renders/

  # Render with larger scale
  %(prog)s save.sav --output-dir renders/ --scale 4
        """,
    )

    parser.add_argument(
        "save_path",
        type=Path,
        help="Path to .sav file",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("renders"),
        help="Output directory for PNG files (default: renders/)",
    )

    parser.add_argument(
        "--scale",
        type=int,
        default=2,
        choices=range(1, 11),
        help="Pixels per tile, 1-10 (default: 2)",
    )

    args = parser.parse_args()

    # Validate save file exists
    if not args.save_path.exists():
        print(f"Error: Save file not found: {args.save_path}")
        return

    # Render
    print(f"Rendering {args.save_path}...")
    print(f"Output directory: {args.output_dir}")
    print(f"Scale: {args.scale}x")

    renderer = MapRenderer()
    output_files = renderer.render(
        save_path=args.save_path,
        output_dir=args.output_dir,
        scale=args.scale,
    )

    print(f"\nRendered {len(output_files)} asteroid(s):")
    for file_path in output_files:
        print(f"  {file_path}")


if __name__ == "__main__":
    main()
```

**Step 4: Make executable**

Run: `chmod +x examples/render_map.py`

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/integration/test_render_map_cli.py -v`

Expected: PASS (or SKIP if test save not available)

**Step 6: Test manually**

Run: `uv run python examples/render_map.py --help`

Expected: Help text displayed

**Step 7: Commit**

```bash
git add examples/render_map.py tests/integration/
git commit -m "feat(cli): add render_map tool for PNG generation"
```

---

## Task 10: Fix DataTransformer Import

**Files:**
- Modify: `src/oni_save_parser/rendering/pipeline.py`

**Step 1: Add missing import**

Edit `src/oni_save_parser/rendering/pipeline.py`, add at the top:

```python
from typing import Any
```

And update the `_build_output_path` signature:

```python
def _build_output_path(
    self,
    output_dir: Path,
    metadata: "SaveMetadata",  # type: ignore
    asteroid: "AsteroidData",  # type: ignore
) -> Path:
```

Or import the types:

```python
from oni_save_parser.rendering.models import SaveMetadata, AsteroidData
```

And update signature:

```python
def _build_output_path(
    self,
    output_dir: Path,
    metadata: SaveMetadata,
    asteroid: AsteroidData,
) -> Path:
```

**Step 2: Verify with mypy**

Run: `uv run mypy src/oni_save_parser/rendering/pipeline.py`

Expected: No errors

**Step 3: Commit**

```bash
git add src/oni_save_parser/rendering/pipeline.py
git commit -m "fix(rendering): add missing type imports in pipeline"
```

---

## Task 11: Integration Test with Real Save

**Files:**
- Create: `tests/integration/test_full_pipeline.py`

**Step 1: Write integration test**

Create `tests/integration/test_full_pipeline.py`:

```python
"""Full pipeline integration test."""
from pathlib import Path

from PIL import Image

from oni_save_parser.rendering.pipeline import MapRenderer


def test_full_pipeline_with_real_save(tmp_path: Path) -> None:
    """Test complete pipeline with a real save file."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        import pytest
        pytest.skip("Test save file not available")

    output_dir = tmp_path / "output"
    renderer = MapRenderer()

    # Render with scale=1 for speed
    output_files = renderer.render(
        save_path=save_path,
        output_dir=output_dir,
        scale=1,
    )

    # Verify output
    assert len(output_files) > 0

    for file_path in output_files:
        file_path = Path(file_path)
        assert file_path.exists()

        # Verify it's a valid PNG
        img = Image.open(file_path)
        assert img.mode == "RGB"
        assert img.width > 0
        assert img.height > 0

        # Should be asteroid size (typically 256x384 or similar)
        assert img.width >= 100
        assert img.height >= 100
```

**Step 2: Run test**

Run: `uv run pytest tests/integration/test_full_pipeline.py -v`

Expected: PASS (or SKIP)

**Step 3: Commit**

```bash
git add tests/integration/test_full_pipeline.py
git commit -m "test(integration): add full pipeline test with real save"
```

---

## Task 12: Run Full Test Suite

**Step 1: Run all tests**

Run: `uv run pytest -v`

Expected: All tests PASS (or SKIP if test saves unavailable)

**Step 2: Check coverage**

Run: `uv run pytest --cov=src/oni_save_parser/rendering --cov-report=term-missing`

Expected: Coverage > 80%

**Step 3: If coverage low, add missing tests**

Identify uncovered lines and add tests as needed.

**Step 4: Commit any new tests**

```bash
git add tests/
git commit -m "test: improve test coverage for rendering module"
```

---

## Task 13: Type Checking

**Step 1: Run mypy on rendering module**

Run: `uv run mypy src/oni_save_parser/rendering/ src/oni_save_parser/assets/`

Expected: No errors (or minimal)

**Step 2: Fix any type errors**

Add type annotations as needed.

**Step 3: Commit fixes**

```bash
git add src/
git commit -m "fix: add type annotations for mypy compliance"
```

---

## Task 14: Documentation

**Files:**
- Create: `docs/rendering.md`

**Step 1: Write usage documentation**

Create `docs/rendering.md`:

```markdown
# Map Rendering

Render ONI save files to PNG images.

## Quick Start

```bash
# Render a save file
uv run python examples/render_map.py your_save.sav --output-dir renders/

# Larger scale for better detail
uv run python examples/render_map.py your_save.sav --scale 4
```

## Features (Phase 1 MVP)

- Terrain-only rendering
- Fallback color palette (no game assets required)
- Single and multi-asteroid support
- Configurable scale (1-10 pixels per tile)
- PNG output

## Output Files

Files are named: `{colony-name}_cycle-{number}_asteroid-{id}-{name}.png`

Example: `MyColony_cycle-123_asteroid-0-Main.png`

## Architecture

Four-stage pipeline:
1. **Parse**: Load save file with `oni_save_parser`
2. **Transform**: Convert to WorldModel
3. **Layout**: Calculate dimensions (minimal in Phase 1)
4. **Render**: Generate PNG with Pillow

## Programmatic Usage

```python
from pathlib import Path
from oni_save_parser.rendering.pipeline import MapRenderer

renderer = MapRenderer()
output_files = renderer.render(
    save_path=Path("save.sav"),
    output_dir=Path("renders/"),
    scale=2,
)

print(f"Created {len(output_files)} images")
```

## Future Phases

- Phase 2: Multi-asteroid layout options
- Phase 3: Building and entity icons
- Phase 4: Game asset extraction for accurate colors
- Phase 5: Comparison/diff tools
- Phase 6: Interactive HTML viewer
```

**Step 2: Update main README**

Add rendering section to main README.md (if exists).

**Step 3: Commit**

```bash
git add docs/rendering.md
git commit -m "docs: add rendering usage documentation"
```

---

## Task 15: Final Verification

**Step 1: Clean test run**

Run: `uv run pytest -v --tb=short`

Expected: All tests pass

**Step 2: Manual test with real save**

Run: `uv run python examples/render_map.py test_saves/01-early-game-cycle-010.sav --output-dir /tmp/test-render`

Expected: PNG created, visually inspect it

**Step 3: Verify git status clean**

Run: `git status`

Expected: Clean working directory

**Step 4: Final commit if needed**

```bash
git add .
git commit -m "chore: final cleanup for Phase 1 MVP"
```

---

## Completion Checklist

- [ ] All unit tests passing
- [ ] Integration tests passing (or skipping gracefully)
- [ ] Type checking passes with mypy
- [ ] Test coverage > 80%
- [ ] CLI tool works with real save files
- [ ] Documentation written
- [ ] Code follows DRY and YAGNI principles
- [ ] Commits are atomic and well-described
- [ ] Phase 1 MVP complete: terrain-only rendering works

## Next Steps

After Phase 1 complete, review work using @superpowers:requesting-code-review, then proceed to Phase 2 (multi-asteroid support) or Phase 3 (buildings/entities).
