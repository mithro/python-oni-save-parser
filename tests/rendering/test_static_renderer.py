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
