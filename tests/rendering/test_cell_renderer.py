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
