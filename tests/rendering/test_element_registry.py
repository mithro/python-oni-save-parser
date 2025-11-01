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
